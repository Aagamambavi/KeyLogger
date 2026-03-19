# 🛡️ Detection & Mitigation Guide: Project KeyLogger

This document outlines the technical methods for detecting, analyzing, and mitigating the activities of the **Educational KeyLogger**. Understanding these defensive measures is a core component of "Purple Team" security operations.

---

## 1. Indicators of Compromise (IoCs)
IoCs are technical artifacts that suggest a system may be compromised. For this project, the following indicators can be monitored:

### Host-Based Indicators
* **Process Monitoring:** Look for unexpected Python instances (`python.exe` or `pythonw.exe`) running with no visible window or attached to high-frequency input polling.
* **File System Artifacts:**
    * **Logs:** Presence of `keylogger.log` in application or temp directories.
    * **Staging:** Creation of a `local_backups/` folder containing JSON files.
* **Persistence:** Check for entries in Windows Registry `Run` keys or Startup folders that point to the `main.py` entry point.

### Network-Based Indicators
* **DNS Queries:** Unusual requests to `smtp.gmail.com` (reporting) or `mongodb.net` (data storage).
* **Outbound Traffic:** Periodic spikes in encrypted traffic over Port **587** (SMTP) or **27017** (MongoDB).

---

## 2. Behavioral Detection Strategies
Behavioral detection focuses on the actions taken by the software rather than matching a specific file signature.

### API Hooking & Input Monitoring
The project utilizes the `pynput` library, which interfaces with low-level system hooks.
* **Detection:** Security tools can monitor for `SetWindowsHookEx` calls (specifically `WH_KEYBOARD_LL` and `WH_MOUSE_LL`).
* **EDR Alerts:** Modern Endpoint Detection and Response (EDR) systems will flag non-standard processes requesting "Input Monitoring" permissions or "Accessibility" features.

### Heuristic Analysis
* **Idle Detection Logic:** A process that remains dormant for long periods but maintains an active handle on input devices is a high-confidence indicator of a logger.
* **Data Exfiltration Patterns:** Identifying a process that aggregates user data and attempts to "phone home" via SMTP or Database protocols at set intervals.

---

## 3. Mitigation & Hardening
To prevent or neutralize the impact of unauthorized monitoring tools, implement the following security controls:

### Technical Controls
* **Egress Filtering:** Implement strict firewall rules to block outbound traffic on common exfiltration ports (587, 465, 27017) for all non-authorized applications.
* **Least Privilege:** Ensure users do not run daily tasks with Administrative privileges, limiting the logger's ability to persist in system-protected directories.
* **Multi-Factor Authentication (MFA):** **MFA is the strongest defense.** Even if a password is captured by a keylogger, the attacker cannot access the account without the second, time-sensitive factor.

### System Configuration
* **Application Whitelisting:** Use tools like AppLocker or Windows Defender Application Control (WDAC) to ensure only verified, signed software can execute on the endpoint.
* **Anti-Keylogging Software:** Utilize security suites that encrypt keystrokes at the kernel level or inject "noise" into the input stream.

---

## 4. Summary for Security Analysts
When investigating a potential infection related to this tool:
1.  **Isolate the Host:** Disconnect from the network to stop data exfiltration to MongoDB/Gmail.
2.  **Audit Credentials:** Check the `.env` file for leaked SMTP or Database credentials to determine where data was sent.
3.  **Analyze Scope:** Review the `local_backups/` folder to identify exactly what data (keystrokes, mouse patterns) was captured before exfiltration.

---
*This document is for educational and research purposes only.*