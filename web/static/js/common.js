/**
 * FNewsCrawler 公共JavaScript函数
 * 
 * 提供通用的工具函数和UI交互功能
 */

// 全局配置
const CONFIG = {
    API_BASE_URL: '/api',
    MESSAGE_TIMEOUT: 5000,
    REFRESH_INTERVAL: 10000
};

// 消息提示函数
function showMessage(message, type = 'info', timeout = CONFIG.MESSAGE_TIMEOUT) {
    const container = document.getElementById('message-container');
    if (!container) {
        console.warn('Message container not found');
        return;
    }
    
    // 创建消息元素
    const messageId = 'message-' + Date.now();
    const alertClass = `alert alert-${type} alert-dismissible fade show`;
    
    const messageHtml = `
        <div id="${messageId}" class="${alertClass}" role="alert">
            <i class="fas fa-${getMessageIcon(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', messageHtml);
    
    // 自动隐藏消息
    if (timeout > 0) {
        setTimeout(() => {
            const messageElement = document.getElementById(messageId);
            if (messageElement) {
                const alert = bootstrap.Alert.getOrCreateInstance(messageElement);
                alert.close();
            }
        }, timeout);
    }
}

// 获取消息图标
function getMessageIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'times-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle',
        'primary': 'info-circle',
        'secondary': 'info-circle',
        'light': 'info-circle',
        'dark': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// 确认对话框
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 格式化时间
function formatTime(seconds) {
    if (seconds < 60) {
        return `${seconds}秒`;
    } else if (seconds < 3600) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}分${remainingSeconds}秒`;
    } else {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return `${hours}时${minutes}分`;
    }
}

// 格式化日期时间
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// 复制到剪贴板
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showMessage('已复制到剪贴板', 'success', 2000);
    } catch (err) {
        // 降级方案
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showMessage('已复制到剪贴板', 'success', 2000);
        } catch (err) {
            showMessage('复制失败', 'danger', 2000);
        }
        document.body.removeChild(textArea);
    }
}

// 下载文件
function downloadFile(content, filename, contentType = 'text/plain') {
    const blob = new Blob([content], { type: contentType });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// 防抖函数
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 验证URL格式
function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

// 验证邮箱格式
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// 生成随机ID
function generateId(length = 8) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

// 加载状态管理
class LoadingManager {
    constructor() {
        this.loadingStates = new Set();
    }
    
    show(elementId, text = '加载中...') {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        this.loadingStates.add(elementId);
        
        const loadingHtml = `
            <div class="text-center py-4" data-loading="true">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 text-muted">${text}</p>
            </div>
        `;
        
        element.innerHTML = loadingHtml;
    }
    
    hide(elementId) {
        this.loadingStates.delete(elementId);
    }
    
    isLoading(elementId) {
        return this.loadingStates.has(elementId);
    }
}

// 全局加载管理器实例
const loadingManager = new LoadingManager();

// API请求封装
class ApiClient {
    constructor(baseURL = CONFIG.API_BASE_URL) {
        this.baseURL = baseURL;
        this.defaultHeaders = {
            'Content-Type': 'application/json'
        };
    }
    
    async request(method, url, data = null, headers = {}) {
        const config = {
            method: method.toUpperCase(),
            headers: { ...this.defaultHeaders, ...headers }
        };
        
        if (data && (method.toUpperCase() === 'POST' || method.toUpperCase() === 'PUT')) {
            config.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(this.baseURL + url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error('API请求失败:', error);
            throw error;
        }
    }
    
    get(url, headers = {}) {
        return this.request('GET', url, null, headers);
    }
    
    post(url, data, headers = {}) {
        return this.request('POST', url, data, headers);
    }
    
    put(url, data, headers = {}) {
        return this.request('PUT', url, data, headers);
    }
    
    delete(url, headers = {}) {
        return this.request('DELETE', url, null, headers);
    }
}

// 全局API客户端实例
const apiClient = new ApiClient();

// 页面可见性检测
function onVisibilityChange(callback) {
    document.addEventListener('visibilitychange', () => {
        callback(!document.hidden);
    });
}

// 网络状态检测
function onNetworkChange(callback) {
    window.addEventListener('online', () => callback(true));
    window.addEventListener('offline', () => callback(false));
}

// 本地存储封装
class Storage {
    static set(key, value, expiry = null) {
        const item = {
            value: value,
            expiry: expiry ? Date.now() + expiry : null
        };
        localStorage.setItem(key, JSON.stringify(item));
    }
    
    static get(key) {
        const itemStr = localStorage.getItem(key);
        if (!itemStr) return null;
        
        try {
            const item = JSON.parse(itemStr);
            
            // 检查是否过期
            if (item.expiry && Date.now() > item.expiry) {
                localStorage.removeItem(key);
                return null;
            }
            
            return item.value;
        } catch (error) {
            console.error('解析存储数据失败:', error);
            localStorage.removeItem(key);
            return null;
        }
    }
    
    static remove(key) {
        localStorage.removeItem(key);
    }
    
    static clear() {
        localStorage.clear();
    }
}

// 初始化函数
function initializeApp() {
    // 设置axios默认配置（如果使用axios）
    if (typeof axios !== 'undefined') {
        axios.defaults.timeout = 30000;
        axios.defaults.headers.common['Content-Type'] = 'application/json';
        
        // 请求拦截器
        axios.interceptors.request.use(
            config => {
                console.log('API请求:', config.method?.toUpperCase(), config.url);
                return config;
            },
            error => {
                console.error('请求错误:', error);
                return Promise.reject(error);
            }
        );
        
        // 响应拦截器
        axios.interceptors.response.use(
            response => {
                console.log('API响应:', response.status, response.config.url);
                return response;
            },
            error => {
                console.error('响应错误:', error);
                if (error.response) {
                    showMessage(`请求失败: ${error.response.status} ${error.response.statusText}`, 'danger');
                } else if (error.request) {
                    showMessage('网络错误，请检查网络连接', 'danger');
                } else {
                    showMessage('请求配置错误', 'danger');
                }
                return Promise.reject(error);
            }
        );
    }
    
    // 监听网络状态
    onNetworkChange(isOnline => {
        if (isOnline) {
            showMessage('网络连接已恢复', 'success', 3000);
        } else {
            showMessage('网络连接已断开', 'warning', 0);
        }
    });
    
    // 设置当前页面导航高亮
    highlightCurrentNavigation();
    
    console.log('FNewsCrawler Web应用初始化完成');
}

// 高亮当前页面导航
function highlightCurrentNavigation() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath !== '/' && href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initializeApp);

// 导出全局对象
window.FNewsCrawler = {
    showMessage,
    confirmAction,
    formatFileSize,
    formatTime,
    formatDateTime,
    copyToClipboard,
    downloadFile,
    debounce,
    throttle,
    isValidUrl,
    isValidEmail,
    generateId,
    loadingManager,
    apiClient,
    Storage
};