import serial
import time
import threading
from datetime import datetime

class SmartParkingController:
    def __init__(self, port='COM3', baud_rate=9600):
        """Initialize the Smart Parking Controller"""
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None
        self.monitoring = False
        self.parking_log = []
        
    def connect(self):
        """Establish serial connection to Arduino"""
        try:
            self.ser = serial.Serial(self.port, self.baud_rate)
            time.sleep(2)  # Wait for Arduino to initialize
            print(f"✅ Connected to Smart Parking System on {self.port}")
            return True
        except serial.SerialException as e:
            print(f"❌ Connection Error: {e}")
            return False
    
    def disconnect(self):
        """Close serial connection"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("🔌 Disconnected from Arduino")
    
    def send_command(self, command):
        """Send command to Arduino"""
        if self.ser and self.ser.is_open:
            self.ser.write(command.encode())
            time.sleep(0.5)
            return True
        else:
            print("❌ No active connection")
            return False
    
    def read_response(self, timeout=2):
        """Read response from Arduino"""
        if not self.ser or not self.ser.is_open:
            return None
            
        start_time = time.time()
        response_lines = []
        
        while time.time() - start_time < timeout:
            if self.ser.in_waiting > 0:
                try:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line:
                        response_lines.append(line)
                        return line  # Return first meaningful response
                except UnicodeDecodeError:
                    continue
            time.sleep(0.1)
        
        return None
    
    def get_parking_status(self):
        """Get current parking status"""
        print("📊 Checking parking status...")
        if self.send_command('s'):
            response = self.read_response()
            if response:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                status = "OCCUPIED" if "OCCUPIED" in response else "AVAILABLE"
                
                # Log the status check
                log_entry = {
                    'timestamp': timestamp,
                    'action': 'STATUS_CHECK',
                    'status': status
                }
                self.parking_log.append(log_entry)
                
                print(f"📍 Current Status: {status}")
                print(f"🕒 Last Updated: {timestamp}")
                return status
        return "Unknown"
    
    def open_gate(self):
        """Open parking barrier gate"""
        confirm = input("🚪 Open barrier gate? (y/n): ").strip().lower()
        if confirm == 'y':
            print("⬆️ Opening barrier gate...")
            if self.send_command('o'):
                response = self.read_response()
                if response and "OPENED" in response:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_entry = {
                        'timestamp': timestamp,
                        'action': 'GATE_OPENED',
                        'status': 'SUCCESS'
                    }
                    self.parking_log.append(log_entry)
                    print("✅ Gate opened successfully!")
                else:
                    print("❌ Failed to open gate")
        else:
            print("❌ Gate opening cancelled")
    
    def close_gate(self):
        """Close parking barrier gate"""
        confirm = input("🚪 Close barrier gate? (y/n): ").strip().lower()
        if confirm == 'y':
            print("⬇️ Closing barrier gate...")
            if self.send_command('c'):
                response = self.read_response()
                if response and "CLOSED" in response:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_entry = {
                        'timestamp': timestamp,
                        'action': 'GATE_CLOSED',
                        'status': 'SUCCESS'
                    }
                    self.parking_log.append(log_entry)
                    print("✅ Gate closed successfully!")
                else:
                    print("❌ Failed to close gate")
        else:
            print("❌ Gate closing cancelled")
    
    def reset_system(self):
        """Reset the parking system"""
        confirm = input("🔄 Reset parking system? (y/n): ").strip().lower()
        if confirm == 'y':
            print("🔄 Resetting system...")
            if self.send_command('r'):
                response = self.read_response()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_entry = {
                    'timestamp': timestamp,
                    'action': 'SYSTEM_RESET',
                    'status': 'SUCCESS'
                }
                self.parking_log.append(log_entry)
                print("✅ System reset complete!")
        else:
            print("❌ System reset cancelled")
    
    def monitor_parking_thread(self):
        """Background thread for monitoring parking"""
        last_status = None
        
        while self.monitoring:
            try:
                if self.ser and self.ser.in_waiting > 0:
                    data = self.ser.readline().decode('utf-8').strip()
                    current_time = datetime.now().strftime("%H:%M:%S")
                    
                    # Check for status changes
                    if "OCCUPIED" in data and last_status != "OCCUPIED":
                        print(f"🚗 [{current_time}] PARKING OCCUPIED")
                        last_status = "OCCUPIED"
                        self.parking_log.append({
                            'timestamp': current_time,
                            'action': 'CAR_PARKED',
                            'status': 'OCCUPIED'
                        })
                    elif "AVAILABLE" in data and last_status != "AVAILABLE":
                        print(f"🟢 [{current_time}] PARKING AVAILABLE")
                        last_status = "AVAILABLE"
                        self.parking_log.append({
                            'timestamp': current_time,
                            'action': 'CAR_LEFT',
                            'status': 'AVAILABLE'
                        })
                    elif "Distance:" in data:
                        print(f"📏 [{current_time}] {data}")
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                break
    
    def start_monitoring(self):
        """Start real-time parking monitoring"""
        if self.monitoring:
            print("⚠️ Monitoring already active!")
            return
            
        print("👀 Starting real-time parking monitoring...")
        print("📱 Press Ctrl+C to stop monitoring")
        print("-" * 50)
        
        self.monitoring = True
        monitor_thread = threading.Thread(target=self.monitor_parking_thread)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            while self.monitoring:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop parking monitoring"""
        self.monitoring = False
        print("\n⏹️ Monitoring stopped")
    
    def view_parking_log(self):
        """Display parking activity log"""
        print("\n📋 PARKING ACTIVITY LOG")
        print("=" * 60)
        
        if not self.parking_log:
            print("📝 No activity logged yet")
            return
        
        # Show last 10 entries
        recent_logs = self.parking_log[-10:]
        
        for log in recent_logs:
            print(f"🕒 {log['timestamp']} | {log['action']} | {log['status']}")
        
        if len(self.parking_log) > 10:
            print(f"\n... and {len(self.parking_log) - 10} more entries")
        
        print("=" * 60)
    
    def display_menu(self):
        """Display main menu"""
        print("\n🅿️ === SMART PARKING CONTROL SYSTEM ===")
        print("1️⃣  Check parking status")
        print("2️⃣  Open barrier gate")
        print("3️⃣  Close barrier gate")
        print("4️⃣  Monitor parking (real-time)")
        print("5️⃣  View activity log")
        print("6️⃣  Reset system")
        print("7️⃣  Exit")
        print("=" * 40)
    
    def run(self):
        """Main program loop"""
        if not self.connect():
            return
        
        print("🎉 Smart Parking System Ready!")
        
        while True:
            try:
                self.display_menu()
                choice = input("👆 Enter your choice (1-7): ").strip()
                
                if choice == '1':
                    self.get_parking_status()
                    
                elif choice == '2':
                    self.open_gate()
                    
                elif choice == '3':
                    self.close_gate()
                    
                elif choice == '4':
                    self.start_monitoring()
                    
                elif choice == '5':
                    self.view_parking_log()
                    
                elif choice == '6':
                    self.reset_system()
                    
                elif choice == '7':
                    print("👋 Goodbye! Closing connection...")
                    break
                    
                else:
                    print("❌ Invalid choice! Please select 1-7")
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n⚠️ Program interrupted by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
        
        self.disconnect()

def main():
    """Main function to run the Smart Parking Controller"""
    print("🚀 Initializing Smart Parking Control System...")
    
    # You can customize the COM port here
    controller = SmartParkingController(port='COM3', baud_rate=9600)
    controller.run()

if __name__ == "__main__":
    main()
