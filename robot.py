

# HTML page with buttons
html = """<!DOCTYPE html>
<html>
<head>
<title>Pico Controller</title>
<style>
body { font-family: sans-serif; text-align: center; }
button {
  width: 100px; height: 100px; margin: 10px;
  font-size: 20px; border-radius: 20px;
}
.grid {
  display: grid; grid-template-columns: 120px 120px 120px;
  justify-content: center; align-items: center;
}
</style>
<script>
function send(dir) {
  fetch('/action?dir=' + dir);
}
</script>
</head>
<body>
<h2>Pico Control</h2>
<div class="grid">
  <div></div><button onclick="send('up')">↑</button><div></div>
  <button onclick="send('left')">←</button>
  <button onclick="send('center')">●</button>
  <button onclick="send('right')">→</button>
  <div></div><button onclick="send('down')">↓</button><div></div>
</div>
<button onclick="send('stop')">STOP</button>
</body>
</html>
"""
