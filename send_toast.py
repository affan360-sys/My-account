import subprocess
import sys

def send_windows_toast(title="Affan Accounting OS", message="It's 10:00 PM! Don't forget to record all today's transactions."):
    ps_script = f"""
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

    $template = @"
    <toast>
        <visual>
            <binding template="ToastGeneric">
                <text>{title}</text>
                <text>{message}</text>
            </binding>
        </visual>
        <audio src="ms-winsoundevent:Notification.Default" />
    </toast>
"@

    $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
    $xml.LoadXml($template)
    $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Affan Accounting").Show($toast)
    """
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Error sending toast: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    send_windows_toast()

