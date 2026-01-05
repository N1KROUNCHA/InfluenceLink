# Quick Fix for Blank White Page

## Step 1: Check Browser Console
1. Open your browser
2. Press F12 to open DevTools
3. Go to the Console tab
4. Look for any red error messages
5. Share those errors - they'll tell us what's wrong

## Step 2: Verify Dev Server is Running
Make sure you ran:
```bash
cd frontend
npm install
npm run dev
```

You should see:
```
VITE v5.x.x  ready in xxx ms
➜  Local:   http://localhost:3000/
```

## Step 3: Test Simple Version
If still blank, temporarily replace `src/App.jsx` with this simple version:

```jsx
export default function App() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>InfluenceLink Test</h1>
      <p>If you see this, React is working!</p>
    </div>
  )
}
```

If this works, the issue is with routing/components. If it doesn't, there's a build/config issue.

## Step 4: Common Fixes

### Fix 1: Reinstall dependencies
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Fix 2: Check Vite is running
Make sure the terminal shows Vite is running and no errors.

### Fix 3: Check the URL
Make sure you're visiting `http://localhost:3000` (not 8000)

### Fix 4: Clear browser cache
Press Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

## Step 5: Check Network Tab
1. Open DevTools (F12)
2. Go to Network tab
3. Refresh the page
4. Check if `main.jsx` and other files load (should show 200 status)

If files show 404 or fail to load, there's a build issue.

