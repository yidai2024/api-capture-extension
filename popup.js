// Popup script - 处理扩展弹出窗口的逻辑
document.addEventListener('DOMContentLoaded', function() {
  let allRequests = [];
  let currentFilter = 'all';
  let searchTerm = '';
  let isEnabled = true;
  
  // 获取当前tab信息
  chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
    if (tabs[0]) {
      loadRequests(tabs[0].id);
    }
  });
  
  // 加载请求数据
  function loadRequests(tabId) {
    chrome.runtime.sendMessage({
      action: 'getRequests',
      tabId: tabId
    }, function(response) {
      if (response && response.requests) {
        allRequests = response.requests;
        updateStats();
        renderRequests();
      } else {
        showEmptyState();
      }
    });
  }
  
  // 更新统计信息
  function updateStats() {
    const total = allRequests.length;
    const domains = new Set(allRequests.map(r => r.domain)).size;
    const apiCount = allRequests.filter(r => 
      r.apiTypes && r.apiTypes.some(t => ['restful', 'api', 'graphql'].includes(t))
    ).length;
    
    document.getElementById('total-requests').textContent = total;
    document.getElementById('unique-domains').textContent = domains;
    document.getElementById('api-count').textContent = apiCount;
  }
  
  // 渲染请求列表
  function renderRequests() {
    const container = document.getElementById('request-list');
    
    // 过滤请求
    let filtered = allRequests;
    
    if (currentFilter !== 'all') {
      filtered = filtered.filter(r => 
        r.apiTypes && r.apiTypes.includes(currentFilter)
      );
    }
    
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(r => 
        r.url.toLowerCase().includes(term) ||
        (r.apiTypes && r.apiTypes.some(t => t.toLowerCase().includes(term)))
      );
    }
    
    // 排序（最新的在前）
    filtered.sort((a, b) => b.timestamp - a.timestamp);
    
    if (filtered.length === 0) {
      showEmptyState();
      return;
    }
    
    container.innerHTML = '';
    
    filtered.forEach((request, index) => {
      const item = createRequestItem(request, index);
      container.appendChild(item);
    });
  }
  
  // 创建请求项元素
  function createRequestItem(request, index) {
    const item = document.createElement('div');
    item.className = 'request-item';
    item.dataset.index = index;
    
    // 格式化URL显示
    let displayUrl = request.url;
    try {
      const urlObj = new URL(request.url);
      displayUrl = urlObj.pathname + urlObj.search;
      if (displayUrl.length > 50) {
        displayUrl = displayUrl.substring(0, 50) + '...';
      }
    } catch (e) {
      if (displayUrl.length > 50) {
        displayUrl = displayUrl.substring(0, 50) + '...';
      }
    }
    
    // 接口类型标签
    const typesHtml = (request.apiTypes || []).map(type => 
      `<span class="api-type ${type}">${type}</span>`
    ).join('');
    
    // 状态信息
    const status = request.statusCode ? `状态: ${request.statusCode}` : '';
    const duration = request.duration ? `耗时: ${Math.round(request.duration)}ms` : '';
    
    item.innerHTML = `
      <div class="request-header">
        <span class="request-method ${request.method}">${request.method}</span>
        <span class="request-meta">
          ${status}
          ${duration}
        </span>
      </div>
      <div class="request-url">${displayUrl}</div>
      <div class="request-types">${typesHtml}</div>
      <div class="request-details" id="details-${index}">
        <div class="detail-row">
          <div class="detail-label">完整URL</div>
          <div class="detail-value">${request.url}</div>
        </div>
        ${request.path ? `
        <div class="detail-row">
          <div class="detail-label">路径</div>
          <div class="detail-value">${request.path}</div>
        </div>
        ` : ''}
        ${request.domain ? `
        <div class="detail-row">
          <div class="detail-label">域名</div>
          <div class="detail-value">${request.domain}</div>
        </div>
        ` : ''}
        ${request.queryParams && Object.keys(request.queryParams).length > 0 ? `
        <div class="detail-row">
          <div class="detail-label">查询参数</div>
          <div class="detail-value">${JSON.stringify(request.queryParams, null, 2)}</div>
        </div>
        ` : ''}
        ${request.requestBody ? `
        <div class="detail-row">
          <div class="detail-label">请求体</div>
          <div class="detail-value">${typeof request.requestBody === 'string' ? 
            request.requestBody.substring(0, 500) : 
            JSON.stringify(request.requestBody, null, 2).substring(0, 500)}</div>
        </div>
        ` : ''}
        ${request.headerAnalysis ? `
        <div class="detail-row">
          <div class="detail-label">请求头分析</div>
          <div class="detail-value">${JSON.stringify(request.headerAnalysis, null, 2)}</div>
        </div>
        ` : ''}
        ${request.error ? `
        <div class="detail-row">
          <div class="detail-label">错误信息</div>
          <div class="detail-value" style="color: #ff6b6b;">${request.error}</div>
        </div>
        ` : ''}
      </div>
    `;
    
    // 点击展开/收起详情
    item.addEventListener('click', function() {
      const details = document.getElementById(`details-${index}`);
      const isExpanded = details.classList.contains('show');
      
      // 收起所有其他项
      document.querySelectorAll('.request-details.show').forEach(d => {
        d.classList.remove('show');
        d.parentElement.classList.remove('expanded');
      });
      
      if (!isExpanded) {
        details.classList.add('show');
        item.classList.add('expanded');
      }
    });
    
    return item;
  }
  
  // 显示空状态
  function showEmptyState() {
    const container = document.getElementById('request-list');
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">📭</div>
        <div>暂无捕获的请求</div>
        <div style="font-size: 12px; margin-top: 10px; opacity: 0.7;">
          点击页面上的功能按钮，插件会自动捕获所有网络请求
        </div>
      </div>
    `;
  }
  
  // 显示通知
  function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.background = type === 'success' ? '#4CAF50' : '#f44336';
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.style.animation = 'slideUp 0.3s ease reverse';
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }
  
  // 切换捕获状态
  document.getElementById('toggle-capture').addEventListener('click', function() {
    isEnabled = !isEnabled;
    this.textContent = isEnabled ? '启用捕获' : '禁用捕获';
    this.classList.toggle('active', isEnabled);
    
    // 通知content script
    chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, {
          action: 'toggleCapture',
          enabled: isEnabled
        });
      }
    });
    
    showNotification(isEnabled ? '捕获已启用' : '捕获已禁用');
  });
  
  // 刷新数据
  document.getElementById('refresh').addEventListener('click', function() {
    chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
      if (tabs[0]) {
        loadRequests(tabs[0].id);
        showNotification('数据已刷新');
      }
    });
  });
  
  // 清空数据
  document.getElementById('clear-all').addEventListener('click', function() {
    if (confirm('确定要清空所有捕获的请求吗？')) {
      chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
        if (tabs[0]) {
          chrome.runtime.sendMessage({
            action: 'clearRequests',
            tabId: tabs[0].id
          }, function(response) {
            if (response && response.success) {
              allRequests = [];
              updateStats();
              showEmptyState();
              showNotification('数据已清空');
            }
          });
        }
      });
    }
  });
  
  // 搜索功能
  document.getElementById('search-input').addEventListener('input', function(e) {
    searchTerm = e.target.value;
    renderRequests();
  });
  
  // 过滤标签
  document.querySelectorAll('.filter-tab').forEach(tab => {
    tab.addEventListener('click', function() {
      document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      currentFilter = this.dataset.filter;
      renderRequests();
    });
  });
  
  // 监听来自background的消息
  chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === 'newRequest') {
      allRequests.push(request.request);
      updateStats();
      renderRequests();
    } else if (request.action === 'requestCompleted') {
      const index = allRequests.findIndex(r => r.id === request.request.id);
      if (index !== -1) {
        allRequests[index] = { ...allRequests[index], ...request.request };
        renderRequests();
      }
    } else if (request.action === 'requestError') {
      const index = allRequests.findIndex(r => r.id === request.request.id);
      if (index !== -1) {
        allRequests[index] = { ...allRequests[index], ...request.request };
        renderRequests();
      }
    }
    return true;
  });
  
  // 初始化显示
  setTimeout(() => {
    if (allRequests.length === 0) {
      showEmptyState();
    }
  }, 1000);
});