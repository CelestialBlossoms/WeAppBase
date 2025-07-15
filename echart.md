# 前端行为追踪集成示例

## 1. 小程序端集成

### 1.1 创建行为追踪器

```javascript
// utils/behavior-tracker.js

class BehaviorTracker {
  constructor() {
    this.sessionId = this.generateSessionId();
    this.userId = this.getUserId();
    this.baseUrl = 'https://your-api-domain.com';
    this.initTracking();
  }

  // 生成会话ID
  generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  // 获取用户ID
  getUserId() {
    const userInfo = wx.getStorageSync('userInfo');
    return userInfo ? userInfo.user_id : 'anonymous';
  }

  // 获取页面信息
  getPageInfo() {
    const pages = getCurrentPages();
    const currentPage = pages[pages.length - 1];
    return {
      path: currentPage ? currentPage.route : '',
      referrer: pages.length > 1 ? pages[pages.length - 2].route : ''
    };
  }

  // 获取设备信息
  getDeviceInfo() {
    const systemInfo = wx.getSystemInfoSync();
    return {
      platform: systemInfo.platform,
      version: systemInfo.version,
      screen_width: systemInfo.screenWidth,
      screen_height: systemInfo.screenHeight,
      model: systemInfo.model,
      system: systemInfo.system
    };
  }

  // 获取网络信息
  getNetworkInfo() {
    return new Promise((resolve) => {
      wx.getNetworkType({
        success: (res) => {
          resolve({
            network_type: res.networkType
          });
        },
        fail: () => {
          resolve({
            network_type: 'unknown'
          });
        }
      });
    });
  }

  // 初始化追踪
  initTracking() {
    this.trackPageView();
    this.trackUserInteractions();
    this.trackProductEvents();
    this.trackOrderEvents();
  }

  // 页面访问追踪
  trackPageView() {
    const pageInfo = this.getPageInfo();
    this.trackEvent('page_view', '页面访问', {
      page_path: pageInfo.path,
      stay_duration: 0,
      referrer: pageInfo.referrer
    });

    // 记录页面进入时间
    this.pageStartTime = Date.now();
  }

  // 页面离开追踪
  trackPageLeave() {
    if (this.pageStartTime) {
      const stayDuration = Date.now() - this.pageStartTime;
      this.trackEvent('page_leave', '页面离开', {
        page_path: this.getPageInfo().path,
        stay_duration: stayDuration
      });
    }
  }

  // 用户交互追踪
  trackUserInteractions() {
    // 点击事件
    this.trackClickEvents();
    
    // 滚动事件
    this.trackScrollEvents();
    
    // 滑动事件
    this.trackSwipeEvents();
  }

  // 追踪点击事件
  trackClickEvents() {
    // 小程序中通过监听页面事件来追踪点击
    // 在页面的onTap事件中调用
  }

  // 追踪滚动事件
  trackScrollEvents() {
    // 在页面的onScroll事件中调用
  }

  // 追踪滑动事件
  trackSwipeEvents() {
    // 在页面的onSwipe事件中调用
  }

  // 商品事件追踪
  trackProductEvents() {
    // 商品浏览
    this.trackProductView();
    
    // 加入购物车
    this.trackAddToCart();
    
    // 收藏商品
    this.trackFavorite();
    
    // 分享商品
    this.trackShare();
  }

  // 商品浏览
  trackProductView(productId) {
    this.trackEvent('product_view', '商品浏览', {
      product_id: productId,
      page_path: this.getPageInfo().path
    });
  }

  // 加入购物车
  trackAddToCart(productId, quantity = 1) {
    this.trackEvent('add_to_cart', '加入购物车', {
      product_id: productId,
      quantity: quantity,
      page_path: this.getPageInfo().path
    });
  }

  // 收藏商品
  trackFavorite(productId, isAdd = true) {
    const eventType = isAdd ? 'add_to_favorite' : 'remove_from_favorite';
    const eventName = isAdd ? '添加收藏' : '取消收藏';
    
    this.trackEvent(eventType, eventName, {
      product_id: productId,
      page_path: this.getPageInfo().path
    });
  }

  // 分享商品
  trackShare(productId, shareType = 'wechat') {
    this.trackEvent('page_share', '页面分享', {
      product_id: productId,
      share_type: shareType,
      page_path: this.getPageInfo().path
    });
  }

  // 订单事件追踪
  trackOrderEvents() {
    // 创建订单
    this.trackOrderCreate();
    
    // 订单支付
    this.trackOrderPay();
    
    // 订单完成
    this.trackOrderComplete();
  }

  // 创建订单
  trackOrderCreate(orderId, orderAmount) {
    this.trackEvent('order_create', '创建订单', {
      order_id: orderId,
      order_amount: orderAmount,
      page_path: this.getPageInfo().path
    });
  }

  // 订单支付
  trackOrderPay(orderId, paymentMethod) {
    this.trackEvent('order_pay', '订单支付', {
      order_id: orderId,
      payment_method: paymentMethod,
      page_path: this.getPageInfo().path
    });
  }

  // 订单完成
  trackOrderComplete(orderId) {
    this.trackEvent('order_complete', '订单完成', {
      order_id: orderId,
      page_path: this.getPageInfo().path
    });
  }

  // 搜索事件追踪
  trackSearch(keyword, resultCount) {
    this.trackEvent('search', '搜索', {
      keyword: keyword,
      result_count: resultCount,
      page_path: this.getPageInfo().path
    });
  }

  // 搜索结果点击
  trackSearchResultClick(keyword, productId, position) {
    this.trackEvent('search_result_click', '搜索结果点击', {
      keyword: keyword,
      product_id: productId,
      position: position,
      page_path: this.getPageInfo().path
    });
  }

  // 上报事件数据
  trackEvent(eventType, eventName, properties = {}) {
    const eventData = {
      event_type: eventType,
      event_name: eventName,
      session_id: this.sessionId,
      user_id: this.userId,
      page_path: this.getPageInfo().path,
      properties: properties,
      device_info: this.getDeviceInfo(),
      timestamp: Date.now()
    };

    // 发送到后端
    this.sendToServer(eventData);
  }

  // 发送数据到服务器
  sendToServer(eventData) {
    wx.request({
      url: `${this.baseUrl}/api/v1/behavior/track`,
      method: 'POST',
      data: eventData,
      header: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${wx.getStorageSync('token')}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          console.log('行为数据上报成功:', res.data);
        } else {
          console.error('行为数据上报失败:', res);
        }
      },
      fail: (err) => {
        console.error('行为数据上报失败:', err);
        // 可以在这里实现重试机制或本地缓存
      }
    });
  }
}

// 创建全局行为追踪器实例
const behaviorTracker = new BehaviorTracker();

export default behaviorTracker;
```

### 1.2 在页面中使用

```javascript
// pages/product/detail.js

import behaviorTracker from '../../utils/behavior-tracker.js';

Page({
  data: {
    productId: null,
    productInfo: {}
  },

  onLoad(options) {
    const productId = options.id;
    this.setData({ productId });
    
    // 追踪商品浏览
    behaviorTracker.trackProductView(productId);
    
    // 获取商品信息
    this.getProductInfo(productId);
  },

  onUnload() {
    // 追踪页面离开
    behaviorTracker.trackPageLeave();
  },

  // 点击加入购物车
  onAddToCart() {
    const { productId } = this.data;
    const quantity = 1;
    
    // 追踪加入购物车事件
    behaviorTracker.trackAddToCart(productId, quantity);
    
    // 执行加入购物车逻辑
    this.addToCart(productId, quantity);
  },

  // 点击收藏
  onToggleFavorite() {
    const { productId } = this.data;
    const isAdd = !this.data.isFavorite;
    
    // 追踪收藏事件
    behaviorTracker.trackFavorite(productId, isAdd);
    
    // 执行收藏逻辑
    this.toggleFavorite(productId, isAdd);
  },

  // 点击分享
  onShare() {
    const { productId } = this.data;
    
    // 追踪分享事件
    behaviorTracker.trackShare(productId, 'wechat');
    
    // 执行分享逻辑
    this.shareProduct(productId);
  },

  // 点击购买
  onBuyNow() {
    const { productId } = this.data;
    
    // 追踪购买事件
    behaviorTracker.trackEvent('buy_now', '立即购买', {
      product_id: productId,
      page_path: this.route
    });
    
    // 跳转到订单确认页
    wx.navigateTo({
      url: `/pages/order/confirm?product_id=${productId}`
    });
  }
});
```

### 1.3 在订单页面中使用

```javascript
// pages/order/confirm.js

import behaviorTracker from '../../utils/behavior-tracker.js';

Page({
  data: {
    orderId: null,
    orderAmount: 0
  },

  onLoad(options) {
    // 获取订单信息
    this.getOrderInfo(options.order_id);
  },

  // 提交订单
  onSubmitOrder() {
    const { orderId, orderAmount } = this.data;
    
    // 追踪创建订单事件
    behaviorTracker.trackOrderCreate(orderId, orderAmount);
    
    // 执行创建订单逻辑
    this.createOrder(orderId, orderAmount);
  },

  // 支付订单
  onPayOrder() {
    const { orderId } = this.data;
    const paymentMethod = 'wechat_pay';
    
    // 追踪订单支付事件
    behaviorTracker.trackOrderPay(orderId, paymentMethod);
    
    // 执行支付逻辑
    this.payOrder(orderId, paymentMethod);
  }
});
```

## 2. H5端集成

### 2.1 创建行为追踪器

```javascript
// utils/behavior-tracker-h5.js

class BehaviorTrackerH5 {
  constructor() {
    this.sessionId = this.generateSessionId();
    this.userId = this.getUserId();
    this.baseUrl = 'https://your-api-domain.com';
    this.pageStartTime = Date.now();
    this.initTracking();
  }

  // 生成会话ID
  generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  // 获取用户ID
  getUserId() {
    const userInfo = localStorage.getItem('userInfo');
    return userInfo ? JSON.parse(userInfo).user_id : 'anonymous';
  }

  // 获取页面信息
  getPageInfo() {
    return {
      path: window.location.pathname,
      referrer: document.referrer
    };
  }

  // 获取设备信息
  getDeviceInfo() {
    return {
      platform: navigator.platform,
      user_agent: navigator.userAgent,
      screen_width: screen.width,
      screen_height: screen.height,
      language: navigator.language
    };
  }

  // 初始化追踪
  initTracking() {
    this.trackPageView();
    this.trackUserInteractions();
    this.trackProductEvents();
    this.trackOrderEvents();
    
    // 页面离开时追踪
    window.addEventListener('beforeunload', () => {
      this.trackPageLeave();
    });
  }

  // 页面访问追踪
  trackPageView() {
    const pageInfo = this.getPageInfo();
    this.trackEvent('page_view', '页面访问', {
      page_path: pageInfo.path,
      stay_duration: 0,
      referrer: pageInfo.referrer
    });
  }

  // 页面离开追踪
  trackPageLeave() {
    const stayDuration = Date.now() - this.pageStartTime;
    this.trackEvent('page_leave', '页面离开', {
      page_path: this.getPageInfo().path,
      stay_duration: stayDuration
    });
  }

  // 用户交互追踪
  trackUserInteractions() {
    // 点击事件
    document.addEventListener('click', (e) => {
      this.trackClick(e);
    });

    // 滚动事件
    let scrollTimer;
    document.addEventListener('scroll', () => {
      clearTimeout(scrollTimer);
      scrollTimer = setTimeout(() => {
        this.trackScroll();
      }, 1000);
    });
  }

  // 追踪点击事件
  trackClick(e) {
    const element = e.target;
    const elementId = element.id || element.className || element.tagName;
    
    this.trackEvent('click', '点击事件', {
      element_id: elementId,
      click_position: { x: e.clientX, y: e.clientY },
      page_path: this.getPageInfo().path
    });
  }

  // 追踪滚动事件
  trackScroll() {
    const scrollDepth = this.getScrollDepth();
    
    this.trackEvent('scroll', '滚动事件', {
      scroll_depth: scrollDepth,
      page_path: this.getPageInfo().path
    });
  }

  // 获取滚动深度
  getScrollDepth() {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    
    return Math.round((scrollTop + windowHeight) / documentHeight * 100) / 100;
  }

  // 商品事件追踪
  trackProductEvents() {
    // 商品浏览
    this.trackProductView();
    
    // 加入购物车
    this.trackAddToCart();
    
    // 收藏商品
    this.trackFavorite();
    
    // 分享商品
    this.trackShare();
  }

  // 商品浏览
  trackProductView(productId) {
    this.trackEvent('product_view', '商品浏览', {
      product_id: productId,
      page_path: this.getPageInfo().path
    });
  }

  // 加入购物车
  trackAddToCart(productId, quantity = 1) {
    this.trackEvent('add_to_cart', '加入购物车', {
      product_id: productId,
      quantity: quantity,
      page_path: this.getPageInfo().path
    });
  }

  // 收藏商品
  trackFavorite(productId, isAdd = true) {
    const eventType = isAdd ? 'add_to_favorite' : 'remove_from_favorite';
    const eventName = isAdd ? '添加收藏' : '取消收藏';
    
    this.trackEvent(eventType, eventName, {
      product_id: productId,
      page_path: this.getPageInfo().path
    });
  }

  // 分享商品
  trackShare(productId, shareType = 'wechat') {
    this.trackEvent('page_share', '页面分享', {
      product_id: productId,
      share_type: shareType,
      page_path: this.getPageInfo().path
    });
  }

  // 订单事件追踪
  trackOrderEvents() {
    // 创建订单
    this.trackOrderCreate();
    
    // 订单支付
    this.trackOrderPay();
    
    // 订单完成
    this.trackOrderComplete();
  }

  // 创建订单
  trackOrderCreate(orderId, orderAmount) {
    this.trackEvent('order_create', '创建订单', {
      order_id: orderId,
      order_amount: orderAmount,
      page_path: this.getPageInfo().path
    });
  }

  // 订单支付
  trackOrderPay(orderId, paymentMethod) {
    this.trackEvent('order_pay', '订单支付', {
      order_id: orderId,
      payment_method: paymentMethod,
      page_path: this.getPageInfo().path
    });
  }

  // 订单完成
  trackOrderComplete(orderId) {
    this.trackEvent('order_complete', '订单完成', {
      order_id: orderId,
      page_path: this.getPageInfo().path
    });
  }

  // 搜索事件追踪
  trackSearch(keyword, resultCount) {
    this.trackEvent('search', '搜索', {
      keyword: keyword,
      result_count: resultCount,
      page_path: this.getPageInfo().path
    });
  }

  // 搜索结果点击
  trackSearchResultClick(keyword, productId, position) {
    this.trackEvent('search_result_click', '搜索结果点击', {
      keyword: keyword,
      product_id: productId,
      position: position,
      page_path: this.getPageInfo().path
    });
  }

  // 上报事件数据
  trackEvent(eventType, eventName, properties = {}) {
    const eventData = {
      event_type: eventType,
      event_name: eventName,
      session_id: this.sessionId,
      user_id: this.userId,
      page_path: this.getPageInfo().path,
      properties: properties,
      device_info: this.getDeviceInfo(),
      timestamp: Date.now()
    };

    // 发送到后端
    this.sendToServer(eventData);
  }

  // 发送数据到服务器
  sendToServer(eventData) {
    fetch(`${this.baseUrl}/api/v1/behavior/track`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(eventData)
    })
    .then(response => response.json())
    .then(data => {
      if (data.code === 200) {
        console.log('行为数据上报成功:', data);
      } else {
        console.error('行为数据上报失败:', data);
      }
    })
    .catch(error => {
      console.error('行为数据上报失败:', error);
      // 可以在这里实现重试机制或本地缓存
    });
  }
}

// 创建全局行为追踪器实例
const behaviorTracker = new BehaviorTrackerH5();

export default behaviorTracker;
```

### 2.2 在Vue组件中使用

```vue
<!-- components/ProductDetail.vue -->

<template>
  <div class="product-detail">
    <div class="product-info">
      <h1>{{ product.name }}</h1>
      <p class="price">¥{{ product.price }}</p>
      <div class="actions">
        <button @click="addToCart">加入购物车</button>
        <button @click="toggleFavorite">
          {{ isFavorite ? '取消收藏' : '收藏' }}
        </button>
        <button @click="share">分享</button>
        <button @click="buyNow">立即购买</button>
      </div>
    </div>
  </div>
</template>

<script>
import behaviorTracker from '@/utils/behavior-tracker-h5.js';

export default {
  name: 'ProductDetail',
  data() {
    return {
      product: {},
      isFavorite: false
    };
  },
  mounted() {
    // 追踪商品浏览
    behaviorTracker.trackProductView(this.$route.params.id);
    
    // 获取商品信息
    this.getProductInfo();
  },
  beforeDestroy() {
    // 追踪页面离开
    behaviorTracker.trackPageLeave();
  },
  methods: {
    addToCart() {
      const productId = this.$route.params.id;
      const quantity = 1;
      
      // 追踪加入购物车事件
      behaviorTracker.trackAddToCart(productId, quantity);
      
      // 执行加入购物车逻辑
      this.doAddToCart(productId, quantity);
    },
    
    toggleFavorite() {
      const productId = this.$route.params.id;
      const isAdd = !this.isFavorite;
      
      // 追踪收藏事件
      behaviorTracker.trackFavorite(productId, isAdd);
      
      // 执行收藏逻辑
      this.doToggleFavorite(productId, isAdd);
    },
    
    share() {
      const productId = this.$route.params.id;
      
      // 追踪分享事件
      behaviorTracker.trackShare(productId, 'wechat');
      
      // 执行分享逻辑
      this.doShare(productId);
    },
    
    buyNow() {
      const productId = this.$route.params.id;
      
      // 追踪购买事件
      behaviorTracker.trackEvent('buy_now', '立即购买', {
        product_id: productId,
        page_path: this.$route.path
      });
      
      // 跳转到订单确认页
      this.$router.push(`/order/confirm?product_id=${productId}`);
    }
  }
};
</script>
```

## 3. 数据可视化组件

### 3.1 使用ECharts展示数据

```javascript
// components/BehaviorCharts.js

import * as echarts from 'echarts';

export class BehaviorCharts {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.charts = {};
  }

  // 渲染概览图表
  renderOverview(data) {
    const chart = echarts.init(this.container);
    
    const option = {
      title: { text: '用户行为概览' },
      tooltip: { trigger: 'axis' },
      legend: { data: ['活跃用户', '总用户', '事件数'] },
      xAxis: { type: 'category', data: data.dates },
      yAxis: { type: 'value' },
      series: [
        {
          name: '活跃用户',
          type: 'line',
          data: data.activeUsers
        },
        {
          name: '总用户',
          type: 'line',
          data: data.totalUsers
        },
        {
          name: '事件数',
          type: 'bar',
          data: data.eventCounts
        }
      ]
    };
    
    chart.setOption(option);
    this.charts.overview = chart;
  }

  // 渲染漏斗图
  renderFunnel(data) {
    const chart = echarts.init(this.container);
    
    const option = {
      title: { text: data.funnel_name },
      tooltip: { trigger: 'item' },
      series: [{
        name: '转化漏斗',
        type: 'funnel',
        left: '10%',
        top: 60,
        width: '80%',
        height: '80%',
        min: 0,
        max: data.steps[0].step_count,
        minSize: '0%',
        maxSize: '100%',
        sort: 'descending',
        gap: 2,
        label: {
          show: true,
          position: 'inside'
        },
        labelLine: {
          length: 10,
          lineStyle: {
            width: 1,
            type: 'solid'
          }
        },
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 1
        },
        emphasis: {
          label: {
            fontSize: 20
          }
        },
        data: data.steps.map(step => ({
          value: step.step_count,
          name: `${step.step_name} (${step.conversion_rate}%)`
        }))
      }]
    };
    
    chart.setOption(option);
    this.charts.funnel = chart;
  }

  // 渲染用户路径图
  renderUserPath(data) {
    const chart = echarts.init(this.container);
    
    const option = {
      title: { text: '用户路径分析' },
      tooltip: { trigger: 'item' },
      series: [{
        type: 'sankey',
        layout: 'none',
        data: data.nodes,
        links: data.links,
        emphasis: {
          focus: 'adjacency'
        },
        lineStyle: {
          color: 'gradient',
          curveness: 0.5
        }
      }]
    };
    
    chart.setOption(option);
    this.charts.userPath = chart;
  }

  // 渲染商品分析图
  renderProductAnalysis(data) {
    const chart = echarts.init(this.container);
    
    const option = {
      title: { text: '商品行为分析' },
      tooltip: { trigger: 'axis' },
      legend: { data: ['浏览量', '点击量', '加购量', '购买量'] },
      xAxis: { type: 'category', data: data.products },
      yAxis: { type: 'value' },
      series: [
        {
          name: '浏览量',
          type: 'bar',
          data: data.views
        },
        {
          name: '点击量',
          type: 'bar',
          data: data.clicks
        },
        {
          name: '加购量',
          type: 'bar',
          data: data.addToCart
        },
        {
          name: '购买量',
          type: 'bar',
          data: data.purchases
        }
      ]
    };
    
    chart.setOption(option);
    this.charts.productAnalysis = chart;
  }

  // 渲染转化率雷达图
  renderConversionRadar(data) {
    const chart = echarts.init(this.container);
    
    const option = {
      title: { text: '转化率分析' },
      tooltip: { trigger: 'item' },
      radar: {
        indicator: [
          { name: '浏览到点击', max: 100 },
          { name: '点击到加购', max: 100 },
          { name: '加购到购买', max: 100 },
          { name: '浏览到购买', max: 100 },
          { name: '收藏率', max: 100 },
          { name: '分享率', max: 100 }
        ]
      },
      series: [{
        name: '转化率',
        type: 'radar',
        data: [{
          value: [
            data.viewToClick,
            data.clickToCart,
            data.cartToPurchase,
            data.viewToPurchase,
            data.favoriteRate,
            data.shareRate
          ],
          name: '当前转化率'
        }]
      }]
    };
    
    chart.setOption(option);
    this.charts.conversionRadar = chart;
  }

  // 渲染用户画像图
  renderUserPortrait(data) {
    const chart = echarts.init(this.container);
    
    const option = {
      title: { text: '用户画像分析' },
      tooltip: { trigger: 'item' },
      series: [
        {
          name: '活跃度分布',
          type: 'pie',
          radius: '50%',
          data: [
            { value: data.highActive, name: '高活跃用户' },
            { value: data.mediumActive, name: '中活跃用户' },
            { value: data.lowActive, name: '低活跃用户' },
            { value: data.inactive, name: '非活跃用户' }
          ]
        },
        {
          name: '消费能力',
          type: 'pie',
          radius: ['60%', '80%'],
          data: [
            { value: data.highSpender, name: '高消费用户' },
            { value: data.mediumSpender, name: '中消费用户' },
            { value: data.lowSpender, name: '低消费用户' }
          ]
        }
      ]
    };
    
    chart.setOption(option);
    this.charts.userPortrait = chart;
  }

  // 渲染实时数据图
  renderRealTimeData(data) {
    const chart = echarts.init(this.container);
    
    const option = {
      title: { text: '实时用户行为' },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'time' },
      yAxis: { type: 'value' },
      series: [{
        name: '在线用户',
        type: 'line',
        smooth: true,
        data: data.onlineUsers
      }, {
        name: '事件数',
        type: 'line',
        smooth: true,
        data: data.eventCounts
      }]
    };
    
    chart.setOption(option);
    this.charts.realTime = chart;
  }

  // 更新实时数据
  updateRealTimeData(newData) {
    if (this.charts.realTime) {
      this.charts.realTime.setOption({
        series: [{
          data: newData.onlineUsers
        }, {
          data: newData.eventCounts
        }]
      });
    }
  }

  // 销毁图表
  destroy() {
    Object.values(this.charts).forEach(chart => {
      if (chart) {
        chart.dispose();
      }
    });
    this.charts = {};
  }
}
```

### 3.2 在Vue组件中使用图表

```vue
<!-- components/BehaviorDashboard.vue -->

<template>
  <div class="behavior-dashboard">
    <div class="dashboard-header">
      <h1>用户行为分析仪表盘</h1>
      <div class="date-picker">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          @change="onDateChange"
        />
      </div>
    </div>
    
    <div class="dashboard-content">
      <div class="chart-row">
        <div class="chart-container">
          <div id="overview-chart" class="chart"></div>
        </div>
        <div class="chart-container">
          <div id="funnel-chart" class="chart"></div>
        </div>
      </div>
      
      <div class="chart-row">
        <div class="chart-container">
          <div id="product-analysis-chart" class="chart"></div>
        </div>
        <div class="chart-container">
          <div id="conversion-radar-chart" class="chart"></div>
        </div>
      </div>
      
      <div class="chart-row">
        <div class="chart-container">
          <div id="user-portrait-chart" class="chart"></div>
        </div>
        <div class="chart-container">
          <div id="real-time-chart" class="chart"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { BehaviorCharts } from '@/components/BehaviorCharts.js';
import { getBehaviorData } from '@/api/behavior.js';

export default {
  name: 'BehaviorDashboard',
  data() {
    return {
      dateRange: [],
      charts: null,
      realTimeTimer: null
    };
  },
  mounted() {
    this.initCharts();
    this.loadData();
    this.startRealTimeUpdate();
  },
  beforeDestroy() {
    this.stopRealTimeUpdate();
    if (this.charts) {
      this.charts.destroy();
    }
  },
  methods: {
    initCharts() {
      this.charts = new BehaviorCharts();
    },
    
    async loadData() {
      try {
        const [overviewData, funnelData, productData, userData] = await Promise.all([
          getBehaviorData('overview', this.dateRange),
          getBehaviorData('funnel', this.dateRange),
          getBehaviorData('product-analysis', this.dateRange),
          getBehaviorData('user-portrait', this.dateRange)
        ]);
        
        this.renderCharts(overviewData, funnelData, productData, userData);
      } catch (error) {
        console.error('加载数据失败:', error);
      }
    },
    
    renderCharts(overviewData, funnelData, productData, userData) {
      // 渲染概览图表
      this.charts.renderOverview(overviewData);
      
      // 渲染漏斗图
      this.charts.renderFunnel(funnelData);
      
      // 渲染商品分析图
      this.charts.renderProductAnalysis(productData);
      
      // 渲染转化率雷达图
      this.charts.renderConversionRadar(productData.conversionRates);
      
      // 渲染用户画像图
      this.charts.renderUserPortrait(userData);
      
      // 渲染实时数据图
      this.charts.renderRealTimeData({
        onlineUsers: [],
        eventCounts: []
      });
    },
    
    startRealTimeUpdate() {
      this.realTimeTimer = setInterval(() => {
        this.updateRealTimeData();
      }, 5000); // 每5秒更新一次
    },
    
    stopRealTimeUpdate() {
      if (this.realTimeTimer) {
        clearInterval(this.realTimeTimer);
        this.realTimeTimer = null;
      }
    },
    
    async updateRealTimeData() {
      try {
        const realTimeData = await getBehaviorData('real-time');
        this.charts.updateRealTimeData(realTimeData);
      } catch (error) {
        console.error('更新实时数据失败:', error);
      }
    },
    
    onDateChange() {
      this.loadData();
    }
  }
};
</script>

<style scoped>
.behavior-dashboard {
  padding: 20px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-container {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart {
  width: 100%;
  height: 400px;
}
</style>
```

## 4. 实时数据监控

### 4.1 WebSocket实时数据推送

```javascript
// utils/real-time-monitor.js

class RealTimeMonitor {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 3000;
    this.callbacks = new Map();
  }

  // 连接WebSocket
  connect(url) {
    try {
      this.ws = new WebSocket(url);
      
      this.ws.onopen = () => {
        console.log('WebSocket连接成功');
        this.reconnectAttempts = 0;
      };
      
      this.ws.onmessage = (event) => {
        this.handleMessage(event.data);
      };
      
      this.ws.onclose = () => {
        console.log('WebSocket连接关闭');
        this.reconnect();
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket连接错误:', error);
      };
      
    } catch (error) {
      console.error('WebSocket连接失败:', error);
    }
  }

  // 处理接收到的消息
  handleMessage(data) {
    try {
      const message = JSON.parse(data);
      const { type, payload } = message;
      
      // 调用对应的回调函数
      if (this.callbacks.has(type)) {
        this.callbacks.get(type)(payload);
      }
      
    } catch (error) {
      console.error('解析消息失败:', error);
    }
  }

  // 订阅事件
  subscribe(eventType, callback) {
    this.callbacks.set(eventType, callback);
    
    // 发送订阅消息
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'subscribe',
        event: eventType
      }));
    }
  }

  // 取消订阅
  unsubscribe(eventType) {
    this.callbacks.delete(eventType);
    
    // 发送取消订阅消息
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'unsubscribe',
        event: eventType
      }));
    }
  }

  // 重连机制
  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect(this.ws.url);
      }, this.reconnectInterval);
    } else {
      console.error('WebSocket重连失败，已达到最大重试次数');
    }
  }

  // 关闭连接
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// 创建全局实时监控实例
const realTimeMonitor = new RealTimeMonitor();

export default realTimeMonitor;
```

### 4.2 实时数据展示组件

```vue
<!-- components/RealTimeMonitor.vue -->

<template>
  <div class="real-time-monitor">
    <div class="monitor-header">
      <h3>实时监控</h3>
      <div class="status-indicator" :class="{ online: isConnected }">
        {{ isConnected ? '在线' : '离线' }}
      </div>
    </div>
    
    <div class="monitor-content">
      <div class="metric-card">
        <div class="metric-title">在线用户</div>
        <div class="metric-value">{{ onlineUsers }}</div>
        <div class="metric-trend" :class="{ up: userTrend > 0, down: userTrend < 0 }">
          {{ Math.abs(userTrend) }}%
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-title">实时事件</div>
        <div class="metric-value">{{ eventCount }}</div>
        <div class="metric-trend" :class="{ up: eventTrend > 0, down: eventTrend < 0 }">
          {{ Math.abs(eventTrend) }}%
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-title">转化率</div>
        <div class="metric-value">{{ conversionRate }}%</div>
        <div class="metric-trend" :class="{ up: conversionTrend > 0, down: conversionTrend < 0 }">
          {{ Math.abs(conversionTrend) }}%
        </div>
      </div>
    </div>
    
    <div class="recent-events">
      <h4>最近事件</h4>
      <div class="event-list">
        <div v-for="event in recentEvents" :key="event.id" class="event-item">
          <div class="event-time">{{ formatTime(event.timestamp) }}</div>
          <div class="event-type">{{ event.event_name }}</div>
          <div class="event-user">{{ event.user_id }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import realTimeMonitor from '@/utils/real-time-monitor.js';

export default {
  name: 'RealTimeMonitor',
  data() {
    return {
      isConnected: false,
      onlineUsers: 0,
      eventCount: 0,
      conversionRate: 0,
      userTrend: 0,
      eventTrend: 0,
      conversionTrend: 0,
      recentEvents: []
    };
  },
  mounted() {
    this.initRealTimeMonitor();
  },
  beforeDestroy() {
    realTimeMonitor.disconnect();
  },
  methods: {
    initRealTimeMonitor() {
      // 连接WebSocket
      realTimeMonitor.connect('ws://your-api-domain.com/ws/behavior');
      
      // 订阅实时数据
      realTimeMonitor.subscribe('online_users', this.updateOnlineUsers);
      realTimeMonitor.subscribe('event_count', this.updateEventCount);
      realTimeMonitor.subscribe('conversion_rate', this.updateConversionRate);
      realTimeMonitor.subscribe('recent_events', this.updateRecentEvents);
    },
    
    updateOnlineUsers(data) {
      this.onlineUsers = data.current;
      this.userTrend = data.trend;
    },
    
    updateEventCount(data) {
      this.eventCount = data.current;
      this.eventTrend = data.trend;
    },
    
    updateConversionRate(data) {
      this.conversionRate = data.current;
      this.conversionTrend = data.trend;
    },
    
    updateRecentEvents(data) {
      this.recentEvents = data.events.slice(0, 10); // 只显示最近10个事件
    },
    
    formatTime(timestamp) {
      const date = new Date(timestamp);
      return date.toLocaleTimeString();
    }
  }
};
</script>

<style scoped>
.real-time-monitor {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.status-indicator {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  background: #f5f5f5;
  color: #666;
}

.status-indicator.online {
  background: #e8f5e8;
  color: #52c41a;
}

.monitor-content {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.metric-card {
  flex: 1;
  text-align: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.metric-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.metric-trend {
  font-size: 12px;
  color: #666;
}

.metric-trend.up {
  color: #52c41a;
}

.metric-trend.down {
  color: #ff4d4f;
}

.recent-events h4 {
  margin-bottom: 12px;
}

.event-list {
  max-height: 200px;
  overflow-y: auto;
}

.event-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.event-time {
  font-size: 12px;
  color: #999;
  width: 80px;
}

.event-type {
  flex: 1;
  margin: 0 12px;
}

.event-user {
  font-size: 12px;
  color: #666;
  width: 100px;
}
</style>
```

## 5. 总结

### 5.1 集成要点

1. **数据收集完整性**
   - 确保所有关键用户行为都被追踪
   - 收集足够的上下文信息（页面路径、设备信息等）
   - 实现数据上报的重试机制

2. **性能优化**
   - 使用批量上报减少网络请求
   - 实现本地缓存机制
   - 优化数据压缩和传输

3. **隐私保护**
   - 遵循数据保护法规
   - 实现用户数据匿名化
   - 提供用户选择退出机制

4. **实时性要求**
   - 使用WebSocket实现实时数据推送
   - 实现断线重连机制
   - 优化数据更新频率

### 5.2 最佳实践

1. **事件命名规范**
   - 使用统一的命名规范
   - 事件名称要清晰易懂
   - 避免敏感信息泄露

2. **数据质量保证**
   - 实现数据验证机制
   - 监控数据完整性
   - 建立数据异常告警

3. **用户体验**
   - 确保追踪不影响页面性能
   - 提供数据收集说明
   - 实现渐进式功能启用

4. **系统可扩展性**
   - 设计模块化的追踪系统
   - 支持自定义事件定义
   - 预留扩展接口

通过以上集成方案，可以为商城小程序提供完整的用户行为分析能力，帮助运营团队更好地理解用户需求，优化产品体验，提升转化率。