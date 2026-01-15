# MT5 Terminal Setup Guide for StructureScout

## 📋 **Required MT5 Configuration**

### **1. Chart Setup**
- **Symbol**: NAS100 (or your broker's equivalent like #NAS100_Mar)
- **Timeframe**: M5 (5-minute charts) - **THIS IS CRITICAL**
- **Chart Type**: Candlestick (recommended)

### **2. MT5 Window Configuration**
- **Window Title**: Must be exactly "MetaTrader 5" (default)
- **Position**: Keep MT5 window visible on screen
- **Size**: Minimum 1200x800 pixels for optimal screenshot capture

### **3. Chart Display Settings**
```
Right-click chart → Properties → Common tab:
✓ Show OHLC values
✓ Show object descriptions
✓ Show price on chart
✓ Show period separators

Colors tab:
✓ Use clear, high-contrast colors
✓ Background: White or light gray
✓ Candlesticks: Green/Red or Blue/Red
```

### **4. Reference Lines (Optional but Recommended)**
Add these to your chart for better AI analysis:
- Previous Day High (horizontal line)
- Previous Day Low (horizontal line)  
- VWAP indicator
- Opening Range High/Low (9:30-10:00 AM)

### **5. Indicators to Display**
Keep it minimal - the AI analyzes price structure:
- **Volume** (optional, helps confirm breakouts)
- **VWAP** (for mean reversion setups)
- **No moving averages or oscillators** (the AI doesn't use them)

### **6. Time Zone Settings**
- **MT5 Time**: Should be set to EST/EDT (New York time)
- **Server Time**: Verify it matches US market hours
- **Local Time**: Not critical, but helpful for reference

### **7. Market Watch Setup**
```
Add these symbols to Market Watch:
✓ NAS100 (or equivalent)
✓ Major indices for context (optional)
✓ USD pairs for correlation (optional)
```

## 🖥️ **VPS Display Requirements**

### **For Screenshot Capture to Work:**
1. **MT5 must be running with GUI** (not headless)
2. **Window must be visible** (not minimized)
3. **Screen resolution**: Minimum 1920x1080
4. **Display scaling**: 100% (no scaling)

### **On Windows VPS:**
- Use Remote Desktop with sufficient resolution
- Don't minimize MT5 window
- Consider keeping VPS session active

## 📸 **How Screenshot Capture Works**

### **Process Flow:**
1. **Bot locates MT5 window** using window title
2. **Calibrates chart area** (excludes toolbars/panels)
3. **Captures screenshot** of chart region only
4. **Saves as PNG** in screenshots folder
5. **Sends to GPT-4o-mini** for analysis

### **Screenshot Details:**
- **Size**: 1920x1080 pixels (configurable)
- **Format**: PNG (high quality)
- **Naming**: NAS100_M5_YYYYMMDD_HHMMSS.png
- **Storage**: screenshots/YYYY-MM-DD/

## ⚙️ **Troubleshooting**

### **If Screenshots Fail:**
1. **Check MT5 window title** - must be "MetaTrader 5"
2. **Ensure window is visible** - not minimized
3. **Verify pyautogui permissions** - allow screen access
4. **Check display resolution** - must be sufficient

### **Debug Commands:**
```python
# Test screenshot capture
from modules.chart_screenshot import chart_capture

# Capture full screen for debugging
chart_capture.capture_full_screen()

# Test window location
window_bounds = chart_capture.locate_mt5_window()
print(f"MT5 window: {window_bounds}")
```

### **Common Issues:**
- **"Window not found"** → MT5 not running or wrong title
- **"Blank screenshot"** → Window minimized or covered
- **"Wrong area"** → Calibration needed for chart region

## 🔄 **Automation Tips**

### **MT5 Startup Script (Windows):**
```batch
@echo off
cd "C:\Program Files\N1 Capita lMarkets MetaTrader 5"
start terminal64.exe
timeout /t 10
echo MT5 started
```

### **Keep MT5 Active:**
- Use Windows Task Scheduler to restart MT5 if closed
- Set up auto-login on VPS reboot
- Monitor MT5 process health

## 📊 **Best Practices**

### **For Optimal AI Analysis:**
1. **Clean chart layout** - minimal indicators
2. **Clear price levels** - visible support/resistance
3. **Consistent timeframe** - always M5
4. **Proper scaling** - show enough history (50-100 bars)
5. **Good lighting** - avoid shadows on screen

### **Chart History:**
- Show **last 50-100 candlesticks** (about 4-8 hours)
- This gives enough context for pattern recognition
- Too little history = insufficient context
- Too much history = price too small to see details

### **Time Alignment:**
- Ensure MT5 shows **EST/EDT time**
- Bot operates 9:30 AM - 11:30 AM EST
- Verify time zone alignment with your VPS

---

**Note**: The bot captures screenshots automatically during trading hours. 
Just ensure MT5 is running with the correct chart setup!
