// 创建SVG图标并转换为PNG
// 这个脚本需要在浏览器环境中运行

const iconSizes = [16, 48, 128];
const svgTemplate = (size) => `
<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="${size}" height="${size}" rx="${size * 0.2}" fill="url(#grad)"/>
  <g fill="white" transform="translate(${size * 0.15}, ${size * 0.15})">
    <!-- 搜索图标 -->
    <circle cx="${size * 0.3}" cy="${size * 0.3}" r="${size * 0.2}" stroke="white" stroke-width="${size * 0.05}" fill="none"/>
    <line x1="${size * 0.45}" y1="${size * 0.45}" x2="${size * 0.6}" y2="${size * 0.6}" stroke="white" stroke-width="${size * 0.05}" stroke-linecap="round"/>
    <!-- API文字 -->
    <text x="${size * 0.1}" y="${size * 0.85}" font-family="Arial, sans-serif" font-size="${size * 0.25}" font-weight="bold" fill="white">API</text>
  </g>
</svg>
`;

// 下载SVG为PNG的函数
function downloadSVGAsPNG(svgString, filename) {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  const img = new Image();
  
  const svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
  const url = URL.createObjectURL(svgBlob);
  
  img.onload = function() {
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);
    
    const pngUrl = canvas.toDataURL('image/png');
    const a = document.createElement('a');
    a.href = pngUrl;
    a.download = filename;
    a.click();
    
    URL.revokeObjectURL(url);
  };
  
  img.src = url;
}

// 生成所有尺寸的图标
function generateAllIcons() {
  iconSizes.forEach(size => {
    const svg = svgTemplate(size);
    downloadSVGAsPNG(svg, `icon${size}.png`);
  });
}

// 导出供其他脚本使用
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { generateAllIcons, iconSizes, svgTemplate };
}

// 如果直接运行，生成图标
if (typeof window !== 'undefined') {
  console.log('请在浏览器控制台中运行 generateAllIcons() 来生成图标');
}