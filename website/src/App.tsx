import { useState } from 'react'

interface MockDevice {
  id: string
  name: string
  address: string
  source: 'BLE' | 'PAIRED'
  transport: string
  pairing: string
  rssi: string
  services: string
  statusMessage: string
}

const MOCK_DEVICES: MockDevice[] = [
  {
    id: 'classic:4142FF85AA71',
    name: 'pTron TWS',
    address: '4142FF85AA71',
    source: 'PAIRED',
    transport: 'Classic Bluetooth (BR/EDR)',
    pairing: 'Not paired (cached in Windows AEP registry)',
    rssi: 'N/A (cached offline record)',
    services: 'Audio Sink, Handsfree Profile (cached)',
    statusMessage:
      'Firmware-level renaming is unsupported for this device. Renaming a local Windows alias does NOT modify the broadcast name observed by other phones or laptops.',
  },
  {
    id: 'ble:E45F01A83210',
    name: 'Nearby BLE Earbuds',
    address: 'E4:5F:01:A8:32:10',
    source: 'BLE',
    transport: 'Bluetooth Low Energy (BLE)',
    pairing: 'Not paired (Active broadcast)',
    rssi: '-58 dBm (Strong)',
    services: '3 advertised UUIDs (Battery Service, Audio, Generic)',
    statusMessage:
      'Firmware-level renaming is unsupported for this device. Remote advertised name cannot be safely written without proprietary vendor protocol.',
  },
  {
    id: 'classic:595C22EC8909',
    name: 'pTron TWS (Left)',
    address: '595C22EC8909',
    source: 'PAIRED',
    transport: 'Classic Bluetooth (BR/EDR)',
    pairing: 'Not paired (cached in Windows AEP registry)',
    rssi: 'N/A (cached offline record)',
    services: 'Audio Sink (cached)',
    statusMessage:
      'Firmware-level renaming is unsupported for this device. No command was sent to protect hardware integrity.',
  },
]

export default function App() {
  const [selectedDevice, setSelectedDevice] = useState<MockDevice>(MOCK_DEVICES[0])
  const [renameInput, setRenameInput] = useState('')
  const [renameResult, setRenameResult] = useState<string | null>(null)
  const [copiedHash, setCopiedHash] = useState(false)
  const [copiedCmd, setCopiedCmd] = useState(false)
  const [openFaq, setOpenFaq] = useState<number | null>(0)

  const GITHUB_REPO = 'https://github.com/omb-11/tws-name-changer'
  const DOWNLOAD_URL = 'https://github.com/omb-11/tws-name-changer/releases/latest/download/TWSNameChanger.exe'
  const RELEASE_URL = 'https://github.com/omb-11/tws-name-changer/releases/tag/v1.0.0'
  const SHA256_HASH = '339B7F0C4A3972C17456F48BFCCE625D990085BE9CCDBE9A8D5581D1314814BD'
  const POWERSHELL_CMD = 'Get-FileHash -Path TWSNameChanger.exe -Algorithm SHA256'

  const handleTestRename = () => {
    if (!renameInput.trim()) {
      setRenameResult('Enter a non-empty custom name to check support.')
      return
    }
    setRenameResult(selectedDevice.statusMessage)
  }

  const handleCopyHash = () => {
    navigator.clipboard.writeText(SHA256_HASH)
    setCopiedHash(true)
    setTimeout(() => setCopiedHash(false), 2000)
  }

  const handleCopyCmd = () => {
    navigator.clipboard.writeText(POWERSHELL_CMD)
    setCopiedCmd(true)
    setTimeout(() => setCopiedCmd(false), 2000)
  }

  const toggleFaq = (index: number) => {
    setOpenFaq(openFaq === index ? null : index)
  }

  return (
    <>
      {/* Navigation */}
      <header className="navbar">
        <div className="container nav-inner">
          <a href="#" className="brand">
            <div className="brand-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="m7 7 10 10-5 5V2l5 5L7 17" />
              </svg>
            </div>
            <span>TWS Name Changer</span>
          </a>

          <nav className="nav-links">
            <a href="#features" className="nav-link">Features</a>
            <a href="#preview" className="nav-link">Interactive Preview</a>
            <a href="#how-it-works" className="nav-link">How It Works</a>
            <a href="#download" className="nav-link">Download</a>
            <a href="#limitations" className="nav-link">Limitations</a>
            <a href="#faq" className="nav-link">FAQ</a>
          </nav>

          <div className="nav-actions">
            <a href={GITHUB_REPO} target="_blank" rel="noopener noreferrer" className="btn btn-secondary btn-sm" aria-label="GitHub Repository">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
              </svg>
              <span>GitHub</span>
            </a>
            <a href={DOWNLOAD_URL} className="btn btn-primary btn-sm">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2 2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              <span>Download .exe</span>
            </a>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="badge">
            <span className="badge-dot"></span>
            <span>Version 1.0.0 · Verified Windows 11 Desktop Release</span>
          </div>
          <h1 className="hero-title">
            Transparent Bluetooth Diagnostics <br />
            <span className="text-gradient">&amp; TWS Rename Verification</span>
          </h1>
          <p className="hero-desc">
            Discover live BLE advertisements and Windows paired Classic records with complete technical honesty.
            No false claims, no fake Windows display alias tricks, and zero risk to your hardware.
          </p>

          <div className="hero-cta-group">
            <a href={DOWNLOAD_URL} className="btn btn-primary">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2 2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              <span>Download for Windows (.exe)</span>
            </a>
            <a href={GITHUB_REPO} target="_blank" rel="noopener noreferrer" className="btn btn-secondary">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
              </svg>
              <span>View Source Code</span>
            </a>
          </div>

          <div className="hero-meta">
            <span className="meta-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              Windows 11 / 10 (64-bit)
            </span>
            <span className="meta-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              Standalone Portable Binary (~202 MB)
            </span>
            <span className="meta-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              100% Local &amp; Privacy-First
            </span>
          </div>
        </div>
      </section>

      {/* Interactive Application Preview */}
      <section id="preview" className="preview-section">
        <div className="container">
          <div className="preview-wrapper">
            <div className="window-titlebar">
              <div className="window-dots">
                <span className="dot dot-red"></span>
                <span className="dot dot-yellow"></span>
                <span className="dot dot-green"></span>
              </div>
              <span>TWS Name Changer — Windows 11 Diagnostics (Live Interactive Mockup)</span>
              <span>v1.0.0</span>
            </div>

            <div className="app-mockup">
              {/* Left Pane */}
              <div className="mockup-pane">
                <div className="mockup-header">Discovered Bluetooth Devices (Click to inspect)</div>
                {MOCK_DEVICES.map((dev) => (
                  <div
                    key={dev.id}
                    className={`device-item ${selectedDevice.id === dev.id ? 'active' : ''}`}
                    onClick={() => {
                      setSelectedDevice(dev)
                      setRenameResult(null)
                    }}
                  >
                    <div className="device-title-row">
                      <span>{dev.name}</span>
                      <span className={`badge-tag ${dev.source === 'BLE' ? 'ble' : 'paired'}`}>
                        {dev.source === 'BLE' ? 'BLE Live' : 'Windows Paired'}
                      </span>
                    </div>
                    <div className="device-sub">{dev.address} · {dev.transport}</div>
                  </div>
                ))}
              </div>

              {/* Right Pane */}
              <div className="mockup-pane">
                <div className="mockup-header">Selected Device Inspector</div>
                <div className="detail-row">
                  <span className="detail-label">Name:</span>
                  <span className="detail-val">{selectedDevice.name}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Address:</span>
                  <span className="detail-val" style={{ fontFamily: 'var(--font-mono)' }}>{selectedDevice.address}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Discovery Source:</span>
                  <span className="detail-val">
                    {selectedDevice.source === 'BLE' ? '🟢 Live BLE Advertisement' : '🟡 Windows Paired Classic (Cached)'}
                  </span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Pairing State:</span>
                  <span className="detail-val">{selectedDevice.pairing}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Signal (RSSI):</span>
                  <span className="detail-val">{selectedDevice.rssi}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Rename Capability:</span>
                  <span className="detail-val" style={{ color: '#ef4444' }}>❌ Unsupported</span>
                </div>

                <div style={{ marginTop: '16px' }}>
                  <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
                    <input
                      type="text"
                      placeholder="Enter custom name..."
                      value={renameInput}
                      onChange={(e) => setRenameInput(e.target.value)}
                      style={{
                        flex: 1,
                        padding: '8px 12px',
                        background: 'rgba(0,0,0,0.4)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-sm)',
                        color: '#fff',
                        fontSize: '0.85rem',
                      }}
                    />
                    <button className="btn btn-secondary btn-sm" onClick={handleTestRename}>
                      Check Rename
                    </button>
                  </div>
                  {renameResult && (
                    <div className="status-callout">
                      <strong>Diagnostic Assessment:</strong> {renameResult}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="section">
        <div className="container">
          <div className="section-head">
            <div className="section-tag">Core Capabilities</div>
            <h2 className="section-title">Engineered for Technical Truth</h2>
            <p className="section-desc">
              Most generic tools modify local display aliases and pretend to have renamed your hardware.
              TWS Name Changer delivers genuine hardware transparency.
            </p>
          </div>

          <div className="grid-3">
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M5 12.55a11 11 0 0 1 14.08 0" />
                  <path d="M1.42 9a16 16 0 0 1 21.16 0" />
                  <path d="M8.53 16.11a6 6 0 0 1 6.95 0" />
                  <line x1="12" y1="20" x2="12.01" y2="20" />
                </svg>
              </div>
              <h3 className="feature-title">Real-Time BLE Discovery</h3>
              <p className="feature-desc">
                Leverages the official Windows BLE Advertisement Watcher via Bleak to capture live radio broadcasts
                from nearby devices, extracting RSSI signal strength and advertised service UUIDs.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
                  <line x1="8" y1="21" x2="16" y2="21" />
                  <line x1="12" y1="17" x2="12" y2="21" />
                </svg>
              </div>
              <h3 className="feature-title">Windows Paired Classic Backend</h3>
              <p className="feature-desc">
                Accesses the native Windows Runtime (WinRT) Device Information APIs to enumerate cached Bluetooth Classic (BR/EDR)
                paired records without requiring elevated Administrator permissions.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                  <circle cx="9" cy="7" r="4" />
                  <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                  <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                </svg>
              </div>
              <h3 className="feature-title">Strict Source Differentiation</h3>
              <p className="feature-desc">
                Clearly identifies the difference between an active live broadcast and an offline paired registry entry.
                Never gives the false impression that an offline earbud is nearby.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                </svg>
              </div>
              <h3 className="feature-title">Firmware Safety Guard</h3>
              <p className="feature-desc">
                Enforces conservative safety rules. Unverified devices (like generic JL JieLi or Actions chips) remain strictly
                unsupported to eliminate any risk of bricking firmware or corrupting MAC addresses.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
              </div>
              <h3 className="feature-title">Actionable Error Diagnostics</h3>
              <p className="feature-desc">
                Provides concrete recovery steps for common Windows errors, such as <code>0x800710DF</code> (Bluetooth disabled or service stopped)
                and <code>0x80070005</code> (Windows Privacy Bluetooth access denied).
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                </svg>
              </div>
              <h3 className="feature-title">100% Privacy &amp; Local Storage</h3>
              <p className="feature-desc">
                No telemetry, no background network calls, and no analytics. Configuration and diagnostic logs reside exclusively
                in standard Windows user directory (<code>%LOCALAPPDATA%\TWSNameChanger</code>).
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="section" style={{ background: 'rgba(0,0,0,0.2)' }}>
        <div className="container">
          <div className="section-head">
            <div className="section-tag">Operation Architecture</div>
            <h2 className="section-title">How TWS Name Changer Operates</h2>
            <p className="section-desc">
              Understand the pipeline behind dual-backend discovery and ethical verification.
            </p>
          </div>

          <div className="steps-container">
            <div className="step-card">
              <div className="step-number">01</div>
              <h3 className="feature-title">Concurrent Scanning</h3>
              <p className="feature-desc">
                Initiates independent scans across both Bleak (Windows BLE Advertisement Watcher) and native WinRT paired enumeration.
                If one subsystem encounters an adapter fault, the other continues without wiping observations.
              </p>
            </div>

            <div className="step-card">
              <div className="step-number">02</div>
              <h3 className="feature-title">Synchronous MAC Parsing</h3>
              <p className="feature-desc">
                WinRT Bluetooth IDs are parsed synchronously via regex-free hex extraction. This retrieves device MAC addresses
                without performing blocking async connection handshakes that freeze when earbuds are offline.
              </p>
            </div>

            <div className="step-card">
              <div className="step-number">03</div>
              <h3 className="feature-title">Capability Assessment</h3>
              <p className="feature-desc">
                The provider registry assesses the device against verified hardware profiles. When no official, safe OTA method exists,
                the app reports <em>Unsupported</em> and sends zero arbitrary commands to the radio.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Download Section */}
      <section id="download" className="section">
        <div className="container">
          <div className="download-box">
            <div>
              <div className="badge" style={{ marginBottom: '16px' }}>Official Release Asset</div>
              <h2 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '12px' }}>Download TWS Name Changer</h2>
              <p style={{ color: 'var(--text-muted)', marginBottom: '24px' }}>
                Self-contained, portable Windows 64-bit executable. Requires no installer, no Python environment,
                and no administrator rights.
              </p>

              <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap', marginBottom: '20px' }}>
                <a href={DOWNLOAD_URL} className="btn btn-primary">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2 2v-4" />
                    <polyline points="7 10 12 15 17 10" />
                    <line x1="12" y1="15" x2="12" y2="3" />
                  </svg>
                  <span>Download TWSNameChanger.exe</span>
                </a>
                <a href={RELEASE_URL} target="_blank" rel="noopener noreferrer" className="btn btn-secondary">
                  <span>Release Notes (v1.0.0)</span>
                </a>
              </div>

              <div style={{ fontSize: '0.85rem', color: 'var(--text-dim)' }}>
                <span>Version: <strong>1.0.0</strong></span> · 
                <span style={{ marginLeft: '8px' }}>File Size: <strong>~202 MB</strong></span> · 
                <span style={{ marginLeft: '8px' }}>Platform: <strong>Windows 11 / 10 x64</strong></span>
              </div>
            </div>

            {/* Checksum Card */}
            <div className="checksum-panel">
              <div className="checksum-title">SHA-256 Release Checksum</div>
              <code className="checksum-code">{SHA256_HASH}</code>
              <button className="copy-btn" onClick={handleCopyHash} style={{ width: '100%', marginBottom: '14px' }}>
                {copiedHash ? '✓ Checksum Copied!' : 'Copy SHA-256 Hash'}
              </button>

              <div className="checksum-title" style={{ marginTop: '12px' }}>Verify in PowerShell</div>
              <code className="checksum-code" style={{ color: '#fff', fontSize: '0.7rem' }}>{POWERSHELL_CMD}</code>
              <button className="copy-btn" onClick={handleCopyCmd} style={{ width: '100%' }}>
                {copiedCmd ? '✓ Command Copied!' : 'Copy Verification Command'}
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Limitations & Technical Reality */}
      <section id="limitations" className="section" style={{ background: 'rgba(0,0,0,0.2)' }}>
        <div className="container">
          <div className="section-head">
            <div className="section-tag">Engineering Honesty</div>
            <h2 className="section-title">Bluetooth Limitations &amp; Firmware Safety</h2>
            <p className="section-desc">
              Why genuine TWS renaming cannot be faked with local Windows aliases.
            </p>
          </div>

          <div className="limitations-card">
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '12px', color: '#f59e0b' }}>
              ⚠️ The Truth About Remote Bluetooth Device Renaming
            </h3>
            <p style={{ color: 'var(--text-muted)', marginBottom: '14px', lineHeight: 1.7 }}>
              <strong>Windows Display Aliases vs. Firmware Broadcasts:</strong> When you rename a Bluetooth device
              inside the Windows Settings app, Windows writes a local alias to the PC's registry (<code>DeviceDisplayInfo</code>).
              This does <strong>not</strong> send a radio command to the earbuds. When you connect those earbuds to an iPhone,
              Android device, or another PC, they will still display their original factory name (e.g., <em>pTron TWS</em>).
            </p>
            <p style={{ color: 'var(--text-muted)', marginBottom: '14px', lineHeight: 1.7 }}>
              <strong>Hardware Architecture of Low-Cost TWS Earbuds:</strong> Popular budget earbuds (pTron, Boat, Noise, Mivi,
              built on Actions Semiconductor ATS3015, JL JieLi AC69xx, or Realtek chipsets) store their broadcast name in
              internal flash memory written during factory flashing. Modifying this broadcast name requires proprietary Over-The-Air (OTA)
              flashing commands or specialized vendor tools.
            </p>
            <p style={{ color: 'var(--text-muted)', lineHeight: 1.7 }}>
              <strong>Our Safety Commitment:</strong> TWS Name Changer refuses to send arbitrary, undocumented Bluetooth commands.
              Doing so risks corrupting the earbud's MAC address or rendering it unpairable (bricked). For unverified devices,
              renaming is explicitly marked as <strong>Unsupported</strong>.
            </p>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="section">
        <div className="container">
          <div className="section-head">
            <div className="section-tag">Frequently Asked Questions</div>
            <h2 className="section-title">Common Questions &amp; Troubleshooting</h2>
          </div>

          <div className="faq-grid">
            {[
              {
                q: 'Will this application change the name that other phones or laptops see?',
                a: 'Only if your earbuds use a verified, documented firmware provider. For unsupported devices (including pTron TWS), the app honestly reports that firmware renaming is unsupported. It does not trick you by creating a local Windows display alias.',
              },
              {
                q: 'Why are my pTron earbuds listed as "Unsupported"?',
                a: 'pTron earbuds use generic TWS chipsets (such as JL JieLi or Actions) where the advertised name is baked into flash memory. There is no public, standard Bluetooth specification for rewriting this name without risking hardware damage.',
              },
              {
                q: 'Why do offline or turned-off earbuds appear in the list?',
                a: 'Windows stores paired Bluetooth devices in its native AEP device cache. TWS Name Changer queries this cache to help you diagnose paired devices even when they are not broadcasting. The app labels them as "[Windows Paired]" so you know they are cached records, not live signals.',
              },
              {
                q: 'What should I do if I get error 0x800710DF or 0x80070005?',
                a: 'Error 0x800710DF means your Bluetooth adapter is turned off or its driver is restarting. Toggle Bluetooth off and on in Windows Settings. Error 0x80070005 means Windows Settings > Privacy & Security > Bluetooth is blocking app access; toggle it on to enable device discovery.',
              },
              {
                q: 'Does TWS Name Changer require Administrator privileges?',
                a: 'No. Both BLE discovery and WinRT paired-device enumeration operate under normal standard user permissions. Administrator privileges are never required.',
              },
              {
                q: 'Is this project open-source and free of malware?',
                a: 'Yes. The complete source code, test suite, and build scripts are published transparently on GitHub under the MIT License. The binary is built using a reproducible PyInstaller script without any analytics or cloud tracking.',
              },
            ].map((item, idx) => (
              <div key={idx} className={`faq-item ${openFaq === idx ? 'open' : ''}`}>
                <button className="faq-question" onClick={() => toggleFaq(idx)}>
                  <span>{item.q}</span>
                  <span className="faq-icon">+</span>
                </button>
                {openFaq === idx && <div className="faq-answer">{item.a}</div>}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-top">
            <div>
              <div className="brand" style={{ marginBottom: '12px' }}>
                <div className="brand-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="m7 7 10 10-5 5V2l5 5L7 17" />
                  </svg>
                </div>
                <span>TWS Name Changer</span>
              </div>
              <p className="footer-brand-desc">
                Honest, diagnostic Bluetooth utility for Windows 11. Designed with privacy, transparency, and hardware safety first.
              </p>
            </div>

            <div className="footer-links-group">
              <div>
                <div className="footer-col-title">Project</div>
                <ul className="footer-links">
                  <li><a href={DOWNLOAD_URL} className="footer-link">Download .exe</a></li>
                  <li><a href={RELEASE_URL} target="_blank" rel="noopener noreferrer" className="footer-link">Release Notes</a></li>
                  <li><a href={GITHUB_REPO} target="_blank" rel="noopener noreferrer" className="footer-link">Source Code</a></li>
                </ul>
              </div>

              <div>
                <div className="footer-col-title">Documentation</div>
                <ul className="footer-links">
                  <li><a href={`${GITHUB_REPO}#readme`} target="_blank" rel="noopener noreferrer" className="footer-link">README</a></li>
                  <li><a href={`${GITHUB_REPO}/blob/master/docs/ARCHITECTURE.md`} target="_blank" rel="noopener noreferrer" className="footer-link">Architecture</a></li>
                  <li><a href={`${GITHUB_REPO}/blob/master/docs/FEASIBILITY.md`} target="_blank" rel="noopener noreferrer" className="footer-link">Feasibility Analysis</a></li>
                </ul>
              </div>
            </div>
          </div>

          <div className="footer-bottom">
            <span>© 2026 TWS Name Changer Project. Distributed under the MIT License.</span>
            <span>Windows is a registered trademark of Microsoft Corporation.</span>
          </div>
        </div>
      </footer>
    </>
  )
}
