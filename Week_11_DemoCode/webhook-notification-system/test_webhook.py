"""
Test Script - Kiểm tra hệ thống webhook
Gửi các request thanh toán để test hệ thống
"""
import requests
import json
import time
from datetime import datetime

# URLs của các service
PAYMENT_SERVICE_URL = "http://localhost:5000"
NOTIFICATION_SERVICE_URL = "http://localhost:5001"


def test_payment_service():
    """
    Test thanh toán bình thường
    """
    print("\n" + "="*60)
    print("TEST 1: Process Payment")
    print("="*60)
    
    payment_data = {
        "customer_id": "CUST001",
        "customer_name": "Nguyễn Văn A",
        "amount": 500000,
        "order_id": "ORD001"
    }
    
    print(f"\n📤 Sending payment request:")
    print(json.dumps(payment_data, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(
            f"{PAYMENT_SERVICE_URL}/api/pay",
            json=payment_data,
            timeout=5
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        print(f"Response Data:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        return response.json()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def test_multiple_payments():
    """
    Test multiple thanh toán
    """
    print("\n" + "="*60)
    print("TEST 2: Process Multiple Payments")
    print("="*60)
    
    customers = [
        {"customer_id": "CUST001", "customer_name": "Nguyễn Văn A", "amount": 100000, "order_id": "ORD001"},
        {"customer_id": "CUST002", "customer_name": "Trần Thị B", "amount": 250000, "order_id": "ORD002"},
        {"customer_id": "CUST003", "customer_name": "Phạm Văn C", "amount": 750000, "order_id": "ORD003"},
        {"customer_id": "CUST004", "customer_name": "Hoàng Thị D", "amount": 1500000, "order_id": "ORD004"},
    ]
    
    for i, customer_data in enumerate(customers, 1):
        print(f"\n📤 Sending payment {i}/4:")
        print(f"   Customer: {customer_data['customer_name']}")
        print(f"   Amount: ${customer_data['amount']:,}")
        
        try:
            response = requests.post(
                f"{PAYMENT_SERVICE_URL}/api/pay",
                json=customer_data,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                payment_id = data.get('data', {}).get('payment_id')
                print(f"   ✅ Payment ID: {payment_id}")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        time.sleep(1)  # Delay giữa các request


def check_payment_history():
    """
    Kiểm tra lịch sử thanh toán
    """
    print("\n" + "="*60)
    print("TEST 3: Get Payment History")
    print("="*60)
    
    try:
        response = requests.get(f"{PAYMENT_SERVICE_URL}/api/payments", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Total payments: {len(data.get('data', []))}")
            print(f"\nPayment List:")
            
            for payment in data.get('data', []):
                print(f"\n  Payment ID: {payment.get('payment_id')}")
                print(f"  Customer: {payment.get('customer_name')}")
                print(f"  Amount: ${payment.get('amount'):,}")
                print(f"  Order: {payment.get('order_id')}")
                print(f"  Status: {payment.get('status')}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def check_notification_history():
    """
    Kiểm tra lịch sử thông báo
    """
    print("\n" + "="*60)
    print("TEST 4: Get Notification History")
    print("="*60)
    
    try:
        response = requests.get(f"{NOTIFICATION_SERVICE_URL}/api/notifications", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Total notifications: {data.get('total', 0)}")
            print(f"\nNotification List:")
            
            for notif in data.get('data', []):
                print(f"\n  Notification ID: {notif.get('notification_id')}")
                print(f"  Customer: {notif.get('customer_name')}")
                print(f"  Amount: ${notif.get('amount'):,}")
                print(f"  Channels: {', '.join(notif.get('channels', []))}")
                print(f"  Status: {notif.get('status')}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def check_service_health():
    """
    Kiểm tra trạng thái các service
    """
    print("\n" + "="*60)
    print("TEST 5: Check Service Health")
    print("="*60)
    
    # Check Payment Service
    try:
        response = requests.get(f"{PAYMENT_SERVICE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"\n✅ Payment Service: HEALTHY")
            print(f"   {json.dumps(response.json(), indent=3)}")
    except Exception as e:
        print(f"\n❌ Payment Service: OFFLINE")
        print(f"   Error: {str(e)}")
    
    # Check Notification Service
    try:
        response = requests.get(f"{NOTIFICATION_SERVICE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"\n✅ Notification Service: HEALTHY")
            print(f"   {json.dumps(response.json(), indent=3)}")
    except Exception as e:
        print(f"\n❌ Notification Service: OFFLINE")
        print(f"   Error: {str(e)}")


def main():
    """
    Chạy tất cả các test
    """
    print("\n" + "#"*60)
    print("# WEBHOOK NOTIFICATION SYSTEM - TEST SUITE")
    print("#"*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Kiểm tra trạng thái services
        check_service_health()
        
        # Test thanh toán
        time.sleep(1)
        test_payment_service()
        
        time.sleep(2)
        
        # Test multiple payments
        test_multiple_payments()
        
        time.sleep(1)
        
        # Kiểm tra lịch sử
        check_payment_history()
        check_notification_history()
        
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
    
    print("\n" + "#"*60)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("#"*60 + "\n")


if __name__ == '__main__':
    main()
