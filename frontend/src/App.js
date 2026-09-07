import { useEffect } from "react";

function App() {
  useEffect(() => {
    window.location.replace("/api/");
  }, []);
  return (
    <p data-testid="redirect-note" style={{ fontFamily: "sans-serif", padding: 24 }}>
      Mengalihkan ke aplikasi Report Sales Srikaton…
    </p>
  );
}

export default App;
