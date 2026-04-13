// 存储捕获的API请求
let capturedRequests = [];

// 接口类型识别规则
const apiPatterns = {
  // RESTful API 模式
  restful: [
    /\/api\/v?\d*\//i,
    /\/rest\//i,
    /\/graphql/i,
    /\/oauth\//i,
    /\/auth\//i,
    /\/login/i,
    /\/logout/i,
    /\/users?\//i,
    /\/admin\//i
  ],
  
  // 数据接口模式
  data: [
    /\/data\//i,
    /\/json\//i,
    /\/xml\//i,
    /\/feed\//i,
    /\/rss\//i
  ],
  
  // 文件上传下载
  file: [
    /\/upload/i,
    /\/download/i,
    /\/file\//i,
    /\/media\//i,
    /\/image\//i,
    /\/video\//i,
    /\/audio\//i
  ],
  
  // 统计分析
  analytics: [
    /\/analytics/i,
    /\/tracking/i,
    /\/metrics/i,
    /\/stats/i,
    /\/log\//i,
    /\/event\//i
  ],
  
  // 搜索接口
  search: [
    /\/search/i,
    /\/query/i,
    /\/suggest/i,
    /\/autocomplete/i
  ],
  
  // 第三方服务
  thirdparty: [
    /googleapis\.com/i,
    /facebook\.com.*api/i,
    /twitter\.com.*api/i,
    /github\.com.*api/i,
    /stripe\.com/i,
    /paypal\.com.*api/i
  ]
};

// 识别接口类型
function identifyApiType(url, method, requestBody) {
  const urlLower = url.toLowerCase();
  const types = [];
  
  // 检查URL模式
  for (const [type, patterns] of Object.entries(apiPatterns)) {
    for (const pattern of patterns) {
      if (pattern.test(urlLower)) {
        types.push(type);
        break;
      }
    }
  }
  
  // 根据请求方法判断
  if (method === 'POST' || method === 'PUT' || method === 'PATCH') {
    if (!types.includes('data')) {
      types.push('write');
    }
  } else if (method === 'GET') {
    if (!types.includes('data')) {
      types.push('read');
    }
  } else if (method === 'DELETE') {
    types.push('delete');
  }
  
  // 根据请求体判断
  if (requestBody) {
    try {
      if (typeof requestBody === 'string') {
        const parsed = JSON.parse(requestBody);
        if (parsed.query) {
          types.push('graphql');
        }
      }
    } catch (e) {
      // 不是JSON，可能是表单数据
      if (requestBody.includes('&') && requestBody.includes('=')) {
        types.push('form-data');
      }
    }
  }
  
  // 默认类型
  if (types.length === 0) {
    types.push('api');
  }
  
  return [...new Set(types)]; // 去重
}

// 分析请求头
function analyzeHeaders(headers) {
  const analysis = {};
  
  if (headers) {
    for (const header of headers) {
      const name = header.name.toLowerCase();
      const value = header.value;
      
      if (name === 'content-type') {
        analysis.contentType = value;
        if (value.includes('application/json')) {
          analysis.format = 'json';
        } else if (value.includes('application/xml')) {
          analysis.format = 'xml';
        } else if (value.includes('multipart/form-data')) {
          analysis.format = 'multipart';
        } else if (value.includes('application/x-www-form-urlencoded')) {
          analysis.format = 'form';
        }
      }
      
      if (name === 'authorization') {
        analysis.hasAuth = true;
        if (value.startsWith('Bearer')) {
          analysis.authType = 'Bearer';
        } else if (value.startsWith('Basic')) {
          analysis.authType = 'Basic';
        }
      }
      
      if (name === 'x-requested-with') {
        analysis.isAjax = true;
      }
    }
  }
  
  return analysis;
}

// 监听网络请求
chrome.webRequest.onBeforeRequest.addListener(
  function(details) {
    // 只捕获主页面和子框架的请求，忽略扩展自身的请求
    if (details.tabId === -1 || details.initiator?.startsWith('chrome-extension://')) {
      return;
    }
    
    const request = {
      id: details.requestId,
      url: details.url,
      method: details.method,
      type: details.type,
      timestamp: details.timeStamp,
      tabId: details.tabId,
      requestBody: details.requestBody
    };
    
    // 识别接口类型
    request.apiTypes = identifyApiType(
      details.url, 
      details.method, 
      details.requestBody
    );
    
    // 解析URL获取更多信息
    try {
      const urlObj = new URL(details.url);
      request.domain = urlObj.hostname;
      request.path = urlObj.pathname;
      request.queryParams = Object.fromEntries(urlObj.searchParams);
    } catch (e) {
      console.error('URL解析错误:', e);
    }
    
    capturedRequests.push(request);
    
    // 限制存储数量，避免内存溢出
    if (capturedRequests.length > 1000) {
      capturedRequests = capturedRequests.slice(-500);
    }
    
    // 发送给popup显示
    chrome.runtime.sendMessage({
      action: 'newRequest',
      request: request
    }).catch(() => {
      // popup可能没有打开，忽略错误
    });
    
    return { cancel: false };
  },
  { urls: ["<all_urls>"] },
  ["requestBody"]
);

// 监听响应头
chrome.webRequest.onHeadersReceived.addListener(
  function(details) {
    const request = capturedRequests.find(r => r.id === details.requestId);
    if (request) {
      request.responseHeaders = details.responseHeaders;
      request.statusCode = details.statusCode;
      request.headerAnalysis = analyzeHeaders(details.responseHeaders);
      
      // 更新接口类型基于响应头
      if (request.headerAnalysis.format) {
        if (!request.apiTypes.includes(request.headerAnalysis.format)) {
          request.apiTypes.push(request.headerAnalysis.format);
        }
      }
    }
    return { responseHeaders: details.responseHeaders };
  },
  { urls: ["<all_urls>"] },
  ["responseHeaders"]
);

// 监听请求完成
chrome.webRequest.onCompleted.addListener(
  function(details) {
    const request = capturedRequests.find(r => r.id === details.requestId);
    if (request) {
      request.completed = true;
      request.duration = details.timeStamp - request.timestamp;
      
      // 发送更新信息
      chrome.runtime.sendMessage({
        action: 'requestCompleted',
        request: request
      }).catch(() => {});
    }
  },
  { urls: ["<all_urls>"] }
);

// 监听请求错误
chrome.webRequest.onErrorOccurred.addListener(
  function(details) {
    const request = capturedRequests.find(r => r.id === details.requestId);
    if (request) {
      request.error = details.error;
      request.completed = true;
      
      chrome.runtime.sendMessage({
        action: 'requestError',
        request: request
      }).catch(() => {});
    }
  },
  { urls: ["<all_urls>"] }
);

// 处理来自popup的消息
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === 'getRequests') {
    // 返回当前tab的请求
    const tabRequests = capturedRequests.filter(r => r.tabId === request.tabId);
    sendResponse({ requests: tabRequests });
  } else if (request.action === 'clearRequests') {
    // 清除指定tab的请求
    capturedRequests = capturedRequests.filter(r => r.tabId !== request.tabId);
    sendResponse({ success: true });
  } else if (request.action === 'exportRequests') {
    // 导出请求数据
    const exportData = {
      timestamp: new Date().toISOString(),
      tabId: request.tabId,
      url: request.url,
      requests: capturedRequests.filter(r => r.tabId === request.tabId)
    };
    sendResponse({ data: exportData });
  }
  return true; // 保持消息通道开放
});

// 监听tab关闭，清理数据
chrome.tabs.onRemoved.addListener(function(tabId) {
  capturedRequests = capturedRequests.filter(r => r.tabId !== tabId);
});

console.log('API Capture & Analyzer 扩展已加载');