var GHPATH = '/';
// Choose a different app prefix name
var APP_PREFIX = 'glamgirlx_';
// The version of the cache. Every time you change any of the files
// you need to change this version (version_01, version_02…). 
// If you don't change the version, the service worker will give your
// users the old files!
var VERSION = 'version_05';
// The files to make available for offline use. make sure to add 
// others to this list
var URLS = [
  `${GHPATH}/`,
  `${GHPATH}/favicon.ico`,
  `${GHPATH}/index.html`,
  `${GHPATH}/static/main.js`,
  `${GHPATH}/static/main.css`,
  `${GHPATH}/static/fonts/bootstrap-icons.css`,
  `${GHPATH}/static/prism.js`,
  `${GHPATH}/static/prism.css`,
  `${GHPATH}/static/qrcode.min.js`,
  `${GHPATH}/media/lips.png`,
  `${GHPATH}/media/icons/VK_logo.svg.png`,
  `${GHPATH}/media/icons/pinterest.svg`,
  `${GHPATH}/media/icons/tumblr-logo.svg`
]
