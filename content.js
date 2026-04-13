// Content script - 在页面上下文中运行
// 主要用于监听页面交互和注入UI元素

(function() {
  'use strict';
  
  // 避免重复注入
  if (window.apiCaptureInjected) {
    return;
  }
  window.apiCaptureInjected = true;
  
  // 创建控制面板UI
  function createControlPanel() {
    const panel = document.createElement('div');
    panel.id = 'api-capture-panel';
    panel.innerHTML = `
      <div class="api-capture-header">
        <span>🔍 API 捕获器</span>
        <button id="api-capture-toggle" class="api-capture-btn">启用</button>
      </div>
      <div class="api-capture-stats">
        <div>捕获请求数: <span id="api-capture-count">0</span></div>
        <div>当前页面: <span id="api-capture-url">${window.location.hostname}</span></div>
      </div>
      <div class="api-capture-actions">
        <button id="api-capture-clear" class="api-capture-btn">清空</button>
        <button id="api-capture-export" class="api-capture-btn">导出</button>
        <button id="api-capture-view" class="api-capture-btn">查看详情</button>
      </div>
    `;
    
    // 添加样式
    const style = document.createElement('style');
    style.textContent = `
      #api-capture-panel {
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        min-width: 250px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.3s ease;
      }
      
      #api-capture-panel:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.4);
      }
      
      .api-capture-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(255,255,255,0.3);
      }
      
      .api-capture-header span {
        font-weight: bold;
        font-size: 16px;
      }
      
      .api-capture-stats {
        margin-bottom: 15px;
        line-height: 1.6;
      }
      
      .api-capture-stats div {
        margin-bottom: 5px;
      }
      
      .api-capture-stats span {
        font-weight: bold;
        color: #ffd700;
      }
      
      .api-capture-actions {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }
      
      .api-capture-btn {
        background: rgba(255,255,255,0.2);
        color: white;
        border: 1px solid rgba(255,255,255,0.3);
        padding: 8px 12px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 12px;
        transition: all 0.2s ease;
        backdrop-filter: blur(5px);
      }
      
      .api-capture-btn:hover {
        background: rgba(255,255,255,0.3);
        transform: translateY(-1px);
      }
      
      .api-capture-btn:active {
        transform: translateY(0);
      }
      
      .api-capture-btn.active {
        background: #4CAF50;
        border-color: #45a049;
      }
      
      .api-capture-notification {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #4CAF50;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        z-index: 10001;
        animation: slideIn 0.3s ease;
      }
      
      @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
      }
      
      @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
      }
      
      .pulse {
        animation: pulse 0.5s ease;
      }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(panel);
    
    return panel;
  }
  
  // 显示通知
  function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = 'api-capture-notification';
    notification.textContent = message;
    notification.style.background = type === 'success' ? '#4CAF50' : '#f44336';
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.style.animation = 'slideIn 0.3s ease reverse';
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }
  
  // 更新统计信息
  function updateStats() {
    chrome.runtime.sendMessage({ action: 'getRequests', tabId: -1 }, function(response) {
      if (response && response.requests) {
        const countElement = document.getElementById('api-capture-count');
        if (countElement) {
          countElement.textContent = response.requests.length;
          countElement.parentElement.classList.add('pulse');
          setTimeout(() => countElement.parentElement.classList.remove('pulse'), 500);
        }
      }
    });
  }
  
  // 初始化控制面板
  function initPanel() {
    const panel = createControlPanel();
    let isEnabled = true;
    
    // 切换启用状态
    document.getElementById('api-capture-toggle').addEventListener('click', function() {
      isEnabled = !isEnabled;
      this.textContent = isEnabled ? '启用' : '禁用';
      this.classList.toggle('active', isEnabled);
      
      // 通知background脚本
      chrome.runtime.sendMessage({
        action: 'toggleCapture',
        enabled: isEnabled
      });
      
      showNotification(isEnabled ? 'API捕获已启用' : 'API捕获已禁用');
    });
    
    // 清空请求
    document.getElementById('api-capture-clear').addEventListener('click', function() {
      chrome.runtime.sendMessage({
        action: 'clearRequests',
        tabId: -1
      }, function(response) {
        if (response && response.success) {
          document.getElementById('api-capture-count').textContent = '0';
          showNotification('请求记录已清空');
        }
      });
    });
    
    // 导出数据
    document.getElementById('api-capture-export').addEventListener('click', function() {
      chrome.runtime.sendMessage({
        action: 'exportRequests',
        tabId: -1,
        url: window.location.href
      }, function(response) {
        if (response && response.data) {
          const blob = new Blob([JSON.stringify(response.data, null, 2)], {
            type: 'application/json'
          });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `api-capture-${Date.now()}.json`;
          a.click();
          URL.revokeObjectURL(url);
          showNotification('数据导出成功');
        }
      });
    });
    
    // 查看详情
    document.getElementById('api-capture-view').addEventListener('click', function() {
      // 打开popup窗口查看详情
      chrome.runtime.sendMessage({
        action: 'openPopup'
      });
    });
    
    // 定期更新统计
    setInterval(updateStats, 2000);
    updateStats();
  }
  
  // 页面加载完成后初始化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPanel);
  } else {
    initPanel();
  }
  
  // 监听来自background的消息
  chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === 'newRequest') {
      // 更新请求计数
      updateStats();
      
      // 可以在这里添加实时通知
      if (request.request.apiTypes && request.request.apiTypes.length > 0) {
        const type = request.request.apiTypes[0];
        const method = request.request.method;
        console.log(`[API Capture] ${method} ${request.request.url} - 类型: ${type}`);
      }
    }
    
    if (request.action === 'ping') {
      sendResponse({ status: 'alive' });
    }
    
    return true;
  });
  
  // 拦截XHR请求（备用方案，用于webRequest无法捕获的情况）
  const originalXHROpen = XMLHttpRequest.prototype.open;
  const originalXHRSend = XMLHttpRequest.prototype.send;
  
  XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
    this._captureMethod = method;
    this._captureUrl = url;
    return originalXHROpen.apply(this, arguments);
  };
  
  XMLHttpRequest.prototype.send = function(data) {
    if (window.apiCaptureEnabled !== false) {
      const request = {
        type: 'xhr',
        method: this._captureMethod,
        url: this._captureUrl,
        data: data,
        timestamp: Date.now()
      };
      
      this.addEventListener('load', function() {
        request.status = this.status;
        request.response = this.responseText?.substring(0, 1000); // 限制长度
        console.log('[API Capture] XHR完成:', request);
      });
    }
    
    return originalXHRSend.apply(this, arguments);
  };
  
  // 拦截fetch请求
  const originalFetch = window.fetch;
  
  window.fetch = function(input, init) {
    if (window.apiCaptureEnabled !== false) {
      const request = {
        type: 'fetch',
        method: init?.method || 'GET',
        url: typeof input === 'string' ? input : input.url,
        data: init?.body,
        timestamp: Date.now()
      };
      
      return originalFetch.apply(this, arguments).then(response => {
        request.status = response.status;
        response.clone().text().then(text => {
          request.response = text.substring(0, 1000);
          console.log('[API Capture] Fetch完成:', request);
        });
        return response;
      });
    }
    
    return originalFetch.apply(this, arguments);
  };
  
  console.log('API Capture 内容脚本已加载');
})();