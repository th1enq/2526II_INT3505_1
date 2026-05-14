"""
Notification Service - Dịch vụ thông báo
Nhận webhook từ dịch vụ thanh toán và gửi thông báo cho khách hàng
"""
from flask import Flask, request, jsonify
from datetime import datetime
import json
import os
import threading
import time

import redis

app = Flask(__name__)

# Database giả để lưu trữ các notification
notifications_db = {}
email_jobs_db = {}

# Redis message queue configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
EMAIL_QUEUE_NAME = os.getenv('EMAIL_QUEUE_NAME', 'notification:email_queue')
DEFAULT_CUSTOMER_EMAIL = os.getenv('DEFAULT_CUSTOMER_EMAIL', 'thienchy3305@gmail.com')

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

@app.route('/webhook/payment', methods=['POST'])
def receive_payment_webhook():
    """
    Webhook endpoint để nhận sự kiện thanh toán thành công
    """
    try:
        webhook_data = request.get_json()
        
        if not webhook_data:
            return jsonify({
                'status': 'error',
                'message': 'Invalid JSON payload'
            }), 400
        
        event_type = webhook_data.get('event')
        event_data = webhook_data.get('data', {})
        
        print(f"\n📨 Received webhook event: {event_type}")
        print(f"Payload: {json.dumps(webhook_data, indent=2)}")
        
        # Xử lý sự kiện thanh toán thành công
        if event_type == 'payment.success':
            notification_id = handle_payment_success(event_data)
            
            return jsonify({
                'status': 'success',
                'message': 'Webhook received and processed',
                'notification_id': notification_id
            }), 200
        
        else:
            return jsonify({
                'status': 'error',
                'message': f'Unknown event type: {event_type}'
            }), 400
            
    except Exception as e:
        print(f"❌ Error processing webhook: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/webhook/customer', methods=['POST'])
def receive_customer_webhook():
    """
    Webhook endpoint để nhận sự kiện khách hàng đăng ký thành công.
    Email được đẩy vào Redis queue và worker xử lý bất đồng bộ.
    """
    try:
        webhook_data = request.get_json()

        if not webhook_data:
            return jsonify({
                'status': 'error',
                'message': 'Invalid JSON payload'
            }), 400

        event_type = webhook_data.get('event')
        event_data = webhook_data.get('data', {})

        print(f"\n📨 Received customer webhook event: {event_type}")
        print(f"Payload: {json.dumps(webhook_data, indent=2, ensure_ascii=False)}")

        if event_type == 'customer.registered':
            job_id = enqueue_registration_email(event_data)

            return jsonify({
                'status': 'success',
                'message': 'Registration email job queued',
                'job_id': job_id
            }), 202

        return jsonify({
            'status': 'error',
            'message': f'Unknown event type: {event_type}'
        }), 400

    except redis.RedisError as e:
        print(f"❌ Redis error while queueing email: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Email queue is not available'
        }), 503
    except Exception as e:
        print(f"❌ Error processing customer webhook: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


def enqueue_registration_email(customer_data):
    """
    Đưa email chào mừng vào Redis queue để worker gửi bất đồng bộ.
    """
    job_id = f"EMAIL{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    customer_name = customer_data.get('customer_name', customer_data.get('name', 'Customer'))
    customer_email = customer_data.get('customer_email', customer_data.get('email', DEFAULT_CUSTOMER_EMAIL))

    email_job = {
        'job_id': job_id,
        'event': 'customer.registered',
        'customer_id': customer_data.get('customer_id', ''),
        'customer_name': customer_name,
        'to_email': customer_email,
        'subject': 'Đăng ký tài khoản thành công',
        'body': (
            f"Xin chào {customer_name},\n\n"
            "Tài khoản của bạn đã được đăng ký thành công.\n"
            "Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi."
        ),
        'status': 'queued',
        'created_at': datetime.now().isoformat(),
        'sent_at': None,
        'error': None
    }

    email_jobs_db[job_id] = email_job
    redis_client.rpush(EMAIL_QUEUE_NAME, json.dumps(email_job, ensure_ascii=False))

    print(f"📬 Registration email queued: {job_id}")
    print(f"   To: {customer_email}")

    return job_id


def email_worker():
    """
    Worker nền lấy email job từ Redis queue và gửi email.
    BLPOP giúp worker chờ job mới mà không cần polling liên tục.
    """
    print(f"📮 Email worker listening on Redis queue: {EMAIL_QUEUE_NAME}")

    while True:
        try:
            _, raw_job = redis_client.blpop(EMAIL_QUEUE_NAME)
            email_job = json.loads(raw_job)
            send_registration_email(email_job)
        except redis.RedisError as e:
            print(f"❌ Redis worker error: {str(e)}")
            time.sleep(3)
        except Exception as e:
            print(f"❌ Email worker error: {str(e)}")


def send_registration_email(email_job):
    """
    Demo gửi email. Trong production có thể thay phần print bằng SMTP/provider thật.
    """
    job_id = email_job['job_id']
    email_job['status'] = 'sent'
    email_job['sent_at'] = datetime.now().isoformat()
    email_jobs_db[job_id] = email_job

    print("\n📧 REGISTRATION EMAIL SENT")
    print(f"Job ID: {job_id}")
    print(f"To: {email_job['to_email']}")
    print(f"Subject: {email_job['subject']}")
    print(email_job['body'])


def handle_payment_success(payment_data):
    """
    Xử lý khi thanh toán thành công
    - Lưu notification vào database
    - Tạo message thông báo
    - Gửi email/SMS/Push notification tới khách hàng
    """
    try:
        # Tạo notification record
        notification_id = f"NOTIF{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        customer_name = payment_data.get('customer_name', 'Customer')
        amount = payment_data.get('amount', 0)
        order_id = payment_data.get('order_id', '')
        payment_id = payment_data.get('payment_id', '')
        
        # Tạo message thông báo
        notification_message = f"""
╔════════════════════════════════════════╗
║      💰 PAYMENT CONFIRMATION 💰       ║
╠════════════════════════════════════════╣
║ Customer: {customer_name:<30} ║
║ Amount: ${amount:>30} ║
║ Order ID: {order_id:<28} ║
║ Payment ID: {payment_id:<26} ║
║ Status: SUCCESS ✅                    ║
║ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<20} ║
╚════════════════════════════════════════╝
        """
        
        notification_record = {
            'notification_id': notification_id,
            'payment_id': payment_id,
            'customer_name': customer_name,
            'customer_id': payment_data.get('customer_id', ''),
            'amount': amount,
            'order_id': order_id,
            'message': notification_message,
            'channels': ['email', 'sms', 'push_notification'],
            'status': 'sent',
            'created_at': datetime.now().isoformat()
        }
        
        # Lưu vào database
        notifications_db[notification_id] = notification_record
        
        # Hiển thị thông báo
        print(f"\n✉️  NOTIFICATION CREATED:")
        print(notification_message)
        print(f"📧 Email sent to: {customer_name}@example.com")
        print(f"📱 SMS sent to: +84-xxx-xxx-xxx")
        print(f"🔔 Push notification sent")
        
        return notification_id
        
    except Exception as e:
        print(f"❌ Error handling payment success: {str(e)}")
        raise


@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """
    Lấy danh sách tất cả các notification
    """
    return jsonify({
        'status': 'success',
        'total': len(notifications_db),
        'data': list(notifications_db.values())
    }), 200


@app.route('/api/email-jobs', methods=['GET'])
def get_email_jobs():
    """
    Lấy danh sách các email job đã được queue/xử lý.
    """
    return jsonify({
        'status': 'success',
        'total': len(email_jobs_db),
        'data': list(email_jobs_db.values())
    }), 200


@app.route('/api/email-jobs/<job_id>', methods=['GET'])
def get_email_job(job_id):
    """
    Lấy thông tin chi tiết một email job.
    """
    if job_id in email_jobs_db:
        return jsonify({
            'status': 'success',
            'data': email_jobs_db[job_id]
        }), 200

    return jsonify({
        'status': 'error',
        'message': 'Email job not found'
    }), 404


@app.route('/api/notifications/<notification_id>', methods=['GET'])
def get_notification(notification_id):
    """
    Lấy thông tin chi tiết một notification
    """
    if notification_id in notifications_db:
        return jsonify({
            'status': 'success',
            'data': notifications_db[notification_id]
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'Notification not found'
        }), 404


@app.route('/health', methods=['GET'])
def health():
    """
    Kiểm tra trạng thái dịch vụ
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Notification Service',
        'total_notifications': len(notifications_db),
        'total_email_jobs': len(email_jobs_db),
        'email_queue': EMAIL_QUEUE_NAME,
        'timestamp': datetime.now().isoformat()
    }), 200


if __name__ == '__main__':
    print("🚀 Notification Service starting on port 5001...")
    print("⏳ Waiting for webhook events from payment service...")
    print(f"🔌 Redis URL: {REDIS_URL}")
    threading.Thread(target=email_worker, daemon=True).start()
    app.run(debug=True, port=5001, use_reloader=False)
