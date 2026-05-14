"""
Notification Service - Dịch vụ thông báo
Nhận webhook từ dịch vụ thanh toán và gửi thông báo cho khách hàng
"""
from flask import Flask, request, jsonify
from datetime import datetime
import json

app = Flask(__name__)

# Database giả để lưu trữ các notification
notifications_db = {}

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
        'timestamp': datetime.now().isoformat()
    }), 200


if __name__ == '__main__':
    print("🚀 Notification Service starting on port 5001...")
    print("⏳ Waiting for webhook events from payment service...")
    app.run(debug=True, port=5001)
