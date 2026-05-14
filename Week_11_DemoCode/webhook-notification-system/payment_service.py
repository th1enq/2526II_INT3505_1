"""
Payment Service - Dịch vụ thanh toán
Xử lý thanh toán từ khách hàng và gửi webhook sang dịch vụ thông báo
"""
from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)

# Cấu hình webhook URL của dịch vụ thông báo
NOTIFICATION_SERVICE_WEBHOOK = "http://localhost:5001/webhook/payment"

# Database giả để lưu trữ các payment
payments_db = {}

@app.route('/api/pay', methods=['POST'])
def process_payment():
    """
    Endpoint để xử lý thanh toán
    Expected JSON:
    {
        "customer_id": "CUST001",
        "customer_name": "John Doe",
        "amount": 100000,
        "order_id": "ORD001"
    }
    """
    try:
        data = request.get_json()
        
        # Validate dữ liệu
        required_fields = ['customer_id', 'customer_name', 'amount', 'order_id']
        if not all(field in data for field in required_fields):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields: ' + ', '.join(required_fields)
            }), 400
        
        # Tạo payment record
        payment_id = f"PAY{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        payment_data = {
            'payment_id': payment_id,
            'customer_id': data['customer_id'],
            'customer_name': data['customer_name'],
            'amount': data['amount'],
            'order_id': data['order_id'],
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'method': 'credit_card'
        }
        
        # Lưu vào database
        payments_db[payment_id] = payment_data
        
        # Gửi webhook sang dịch vụ thông báo
        send_webhook(payment_data)
        
        return jsonify({
            'status': 'success',
            'message': 'Payment processed successfully',
            'payment_id': payment_id,
            'data': payment_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


def send_webhook(payment_data):
    """
    Gửi webhook sang dịch vụ thông báo
    """
    try:
        webhook_payload = {
            'event': 'payment.success',
            'timestamp': payment_data['timestamp'],
            'data': payment_data
        }
        
        print(f"\n📤 Sending webhook to notification service...")
        print(f"URL: {NOTIFICATION_SERVICE_WEBHOOK}")
        print(f"Payload: {json.dumps(webhook_payload, indent=2)}")
        
        response = requests.post(
            NOTIFICATION_SERVICE_WEBHOOK,
            json=webhook_payload,
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ Webhook sent successfully! Response: {response.json()}")
        else:
            print(f"❌ Webhook failed! Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"⚠️  Warning: Notification service not available at {NOTIFICATION_SERVICE_WEBHOOK}")
    except Exception as e:
        print(f"❌ Error sending webhook: {str(e)}")


@app.route('/api/payments', methods=['GET'])
def get_payments():
    """
    Lấy danh sách tất cả các payment
    """
    return jsonify({
        'status': 'success',
        'data': list(payments_db.values())
    }), 200


@app.route('/api/payments/<payment_id>', methods=['GET'])
def get_payment(payment_id):
    """
    Lấy thông tin chi tiết một payment
    """
    if payment_id in payments_db:
        return jsonify({
            'status': 'success',
            'data': payments_db[payment_id]
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'Payment not found'
        }), 404


@app.route('/health', methods=['GET'])
def health():
    """
    Kiểm tra trạng thái dịch vụ
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Payment Service',
        'timestamp': datetime.now().isoformat()
    }), 200


if __name__ == '__main__':
    print("🚀 Payment Service starting on port 5000...")
    print(f"📍 Webhook will be sent to: {NOTIFICATION_SERVICE_WEBHOOK}")
    app.run(debug=True, port=5000)
