const chokidar = require('chokidar');
const http = require('http');
const path = require('path');

console.log('🚀 启动文件监视器...');
console.log('📂 监听目录:', path.join(__dirname, '..', 'src', 'enterprise_agent_system'));

// 监听 enterprise_agent_system/src 目录下的文件变化
const watcher = chokidar.watch(path.join(__dirname, '..', 'src', 'enterprise_agent_system'), {
  ignored: /(^|[\/\\])\../, // 忽略隐藏文件
  persistent: true,
  ignoreInitial: true,
  interval: 300,
  binaryInterval: 300
});

// 创建一个简单的HTTP服务器，用于发送更新通知
const connections = new Set();
const server = http.createServer((req, res) => {
  // 设置SSE（Server-Sent Events）响应头
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': '*'
  });

  // 将新连接添加到集合中
  connections.add(res);

  // 客户端断开连接时移除
  req.on('close', () => {
    connections.delete(res);
  });
});

// 文件变化处理函数
const handleFileChange = (type, filePath) => {
  const relativePath = path.relative(path.join(__dirname, '..'), filePath);
  console.log(`📝 文件${type}: ${relativePath}`);
  
  // 向所有连接的客户端发送更新通知
  connections.forEach(res => {
    try {
      res.write(`data: ${JSON.stringify({ type, file: relativePath, timestamp: Date.now() })}\n\n`);
    } catch (e) {
      console.error('发送更新通知失败:', e);
    }
  });
};

// 设置文件监听器
watcher
  .on('add', (path) => handleFileChange('创建', path))
  .on('change', (path) => handleFileChange('修改', path))
  .on('unlink', (path) => handleFileChange('删除', path))
  .on('error', (error) => console.error('❌ 监视错误:', error))
  .on('ready', () => console.log('✅ 监视器已就绪，正在监听文件变化...'));

// 启动服务器
const PORT = 3001;
server.listen(PORT, () => {
  console.log(`🌐 通知服务器已启动，监听端口: ${PORT}`);
  console.log(`\n🎯 使用方法：在浏览器控制台运行: `);
  console.log(`   fetch('http://localhost:${PORT}')`);
  console.log(`\n   或者在HTML中添加EventSource监听器`);
});

// 清理函数
process.on('SIGINT', () => {
  console.log('\n👋 正在停止监视器...');
  watcher.close();
  connections.forEach(res => res.end());
  server.close(() => {
    console.log('✅ 监视器已停止');
    process.exit(0);
  });
});
