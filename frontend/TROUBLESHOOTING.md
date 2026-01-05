# Troubleshooting Blank White Page

If you're seeing a blank white page, follow these steps:

## 1. Check Browser Console
Open browser DevTools (F12) and check the Console tab for errors.

## 2. Install Dependencies
Make sure all dependencies are installed:
```bash
cd frontend
npm install
```

## 3. Check if Dev Server is Running
```bash
npm run dev
```
You should see output like:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
```

## 4. Common Issues

### Issue: Module not found errors
**Solution:** Delete `node_modules` and `package-lock.json`, then reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: Tailwind CSS not working
**Solution:** Make sure `index.css` has Tailwind directives at the top.

### Issue: CORS errors
**Solution:** Make sure your FastAPI backend is running and CORS is enabled.

### Issue: Port already in use
**Solution:** Change the port in `vite.config.js` or kill the process using port 3000.

## 5. Test Basic React
If nothing works, try this simple test in `src/App.jsx`:
```jsx
export default function App() {
  return <div><h1>Hello World</h1></div>
}
```

If this works, the issue is with routing or components.

## 6. Check Network Tab
In DevTools Network tab, check if all files are loading (200 status).

## 7. Clear Browser Cache
Try hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

