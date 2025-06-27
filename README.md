# 📊 Performance Monitoring Suite

🔍 **Comprehensive Linux desktop performance analysis and monitoring tools** for KDE Plasma, VSCode, and system-wide performance optimization.

## 🚀 Features

### **🖥️ KDE Performance Forensics**
- **Memory leak detection** in KDE Plasma components
- **Process analysis** with detailed resource usage
- **Performance bottleneck identification**
- **JSON report generation** with actionable insights

### **⌨️ Typing Delay Analysis**
- **Real-time typing latency measurement**
- **VSCode performance optimization**
- **Augment extension compatibility fixes**
- **Input lag forensics** and resolution

### **🔧 System Monitoring**
- **CPU spike detection** and analysis
- **Persistent monitoring daemon**
- **Enhanced memory API** integration
- **Automated performance reporting**

## 📁 Repository Structure

```
performance-monitoring-suite/
├── kde_performance_forensics.py      # KDE performance analysis tool
├── typing_delay_forensics.py         # Typing latency measurement
├── vscode_cpu_spike_monitor.py       # VSCode CPU monitoring
├── augment_typing_delay_fix.py       # Augment extension fixes
├── start-persistent-monitoring.sh    # Monitoring daemon
├── monitoring/                       # Enhanced monitoring tools
├── kde-monitoring-tools/             # KDE-specific utilities
├── kde_performance_report_*.json     # Sample performance data
└── performance_final_*.png           # Performance visualizations
```

## 🛠️ Installation

### **Prerequisites**
```bash
# Install required Python packages
pip install psutil matplotlib json subprocess

# Install system monitoring tools
sudo dnf install htop iotop nethogs  # Fedora
sudo apt install htop iotop nethogs  # Ubuntu/Debian
```

### **Quick Start**
```bash
# Clone the repository
git clone https://github.com/swipswaps/performance-monitoring-suite.git
cd performance-monitoring-suite

# Make scripts executable
chmod +x start-persistent-monitoring.sh

# Run KDE performance analysis
python3 kde_performance_forensics.py

# Start persistent monitoring
./start-persistent-monitoring.sh
```

## 📈 Usage Examples

### **KDE Performance Analysis**
```bash
# Generate comprehensive KDE performance report
python3 kde_performance_forensics.py

# Output: kde_performance_report_YYYYMMDD_HHMMSS.json
```

### **Typing Delay Measurement**
```bash
# Measure typing latency in real-time
python3 typing_delay_forensics.py

# Fix Augment extension typing delays
python3 augment_typing_delay_fix.py
```

### **VSCode CPU Monitoring**
```bash
# Monitor VSCode CPU usage and spikes
python3 vscode_cpu_spike_monitor.py
```

## 🎯 Key Benefits

- **🔍 Real System Analysis**: No simulations - actual system performance data
- **📊 Professional Reporting**: JSON and visual reports for analysis
- **⚡ Performance Optimization**: Actionable insights for system improvement
- **🛡️ Proactive Monitoring**: Continuous system health tracking
- **🔧 Problem Resolution**: Specific fixes for common performance issues

## 📊 Sample Output

The tools generate detailed performance reports including:
- **Memory usage patterns** and leak detection
- **CPU utilization** and spike analysis
- **Typing latency measurements** with statistical analysis
- **Process resource consumption** breakdown
- **System optimization recommendations**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [kde-memory-guardian](https://github.com/swipswaps/kde-memory-guardian) - KDE memory management
- [log-ui](https://github.com/swipswaps/log-ui) - Professional log analysis interface

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Built with ❤️ for the Linux desktop community**
