import { Link, useNavigate } from "react-router";
import { useState } from "react";

export function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function handleCoordinatorLogin(e: React.FormEvent) {
    e.preventDefault();
    // Demo: any credentials work for coordinator
    navigate("/dashboard");
  }

  return (
    <div className="min-h-screen bg-[#f7f9fc] flex flex-col">
      {/* Minimal nav */}
      <nav className="flex items-center justify-between px-8 py-4">
        <Link to="/" className="text-xl font-bold tracking-tight font-[Inter_Tight] text-[#191c1e]">
          IA SmartMatch
        </Link>
      </nav>

      <div className="flex-1 flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          {/* Logo */}
          <div className="flex flex-col items-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-br from-[#005394] to-[#2b6cb0] rounded-2xl flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h1 className="text-2xl font-[Inter_Tight] font-bold text-[#191c1e]">Welcome Back</h1>
            <p className="text-[#414750] mt-1">Sign in to your IA West account</p>
          </div>

          {/* Role Selection Tabs */}
          <div className="bg-white rounded-2xl shadow-sm border border-[#e0e3e6] overflow-hidden">
            {/* Coordinator Login */}
            <div className="p-8">
              <div className="flex items-center gap-2 mb-6">
                <div className="w-2 h-2 rounded-full bg-[#005394]" />
                <h2 className="font-[Inter_Tight] font-bold text-lg">Coordinator Access</h2>
              </div>

              <form onSubmit={handleCoordinatorLogin} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-[#414750] mb-1.5">Email</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="coordinator@iawest.org"
                    className="w-full px-4 py-3 rounded-xl border border-[#c1c7d2] bg-[#f2f4f7] focus:outline-none focus:ring-2 focus:ring-[#005394] focus:border-transparent transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#414750] mb-1.5">Password</label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter password"
                    className="w-full px-4 py-3 rounded-xl border border-[#c1c7d2] bg-[#f2f4f7] focus:outline-none focus:ring-2 focus:ring-[#005394] focus:border-transparent transition-all"
                  />
                </div>
                <button
                  type="submit"
                  className="w-full bg-gradient-to-r from-[#005394] to-[#2b6cb0] text-white py-3 rounded-xl font-semibold shadow-sm hover:opacity-90 active:scale-[0.98] transition-all"
                >
                  Sign In as Coordinator
                </button>
              </form>
            </div>

            {/* Divider */}
            <div className="border-t border-[#e0e3e6]" />

            {/* Volunteer Login - Coming Soon */}
            <div className="p-8 bg-[#f7f9fc]">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-2 h-2 rounded-full bg-[#414750]" />
                <h2 className="font-[Inter_Tight] font-bold text-lg text-[#414750]">Volunteer Access</h2>
                <span className="ml-auto text-xs font-semibold bg-[#d5e0f7] text-[#005394] px-2 py-0.5 rounded-full">
                  Coming Soon
                </span>
              </div>
              <p className="text-sm text-[#414750] mb-4">
                Volunteer login with LinkedIn integration for experience scraping is under development.
                Contact your coordinator for access.
              </p>
              <button
                disabled
                className="w-full flex items-center justify-center gap-3 py-3 rounded-xl border border-[#c1c7d2] bg-white text-[#414750] font-semibold opacity-50 cursor-not-allowed"
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                </svg>
                Sign In with LinkedIn
              </button>
            </div>
          </div>

          <p className="text-center text-sm text-[#414750] mt-6">
            <Link to="/" className="text-[#005394] font-medium hover:underline">&larr; Back to home</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
