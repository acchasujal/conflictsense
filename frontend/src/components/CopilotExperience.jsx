import React, { useState, useRef } from 'react';
import { uploadFiles } from '../lib/api.js';

export default function CopilotExperience({ onRunAnalysis }) {
  const [activeTab, setActiveTab] = useState('demo'); // 'demo' | 'upload'
  const [files, setFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleUploadAndAnalyze = async () => {
    if (files.length === 0) return;
    setIsUploading(true);
    try {
      await uploadFiles(files);
      onRunAnalysis("custom_upload");
    } catch (e) {
      console.error("Upload failed", e);
      alert("Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div
      style={{
        background: '#FFFFFF',
        border: '1px solid #E2E8F0',
        borderRadius: 12,
        padding: '20px 24px',
        marginBottom: 16,
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      <div style={{
        position: 'absolute',
        top: 0, left: 0, width: '100%', height: '4px',
        background: 'linear-gradient(90deg, #185FA5, #378ADD, #9F8FE8, #185FA5)',
        backgroundSize: '200% 100%',
        animation: 'gradientShift 5s ease infinite'
      }} />

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 20, borderBottom: '1px solid #E2E8F0', marginBottom: 20 }}>
        <div 
          onClick={() => setActiveTab('demo')}
          style={{
            paddingBottom: 8,
            cursor: 'pointer',
            fontWeight: activeTab === 'demo' ? 600 : 400,
            color: activeTab === 'demo' ? '#0F172A' : '#64748B',
            borderBottom: activeTab === 'demo' ? '2px solid #185FA5' : '2px solid transparent',
            transition: 'all 0.2s'
          }}
        >
          Demo Scenarios
        </div>
        <div 
          onClick={() => setActiveTab('upload')}
          style={{
            paddingBottom: 8,
            cursor: 'pointer',
            fontWeight: activeTab === 'upload' ? 600 : 400,
            color: activeTab === 'upload' ? '#0F172A' : '#64748B',
            borderBottom: activeTab === 'upload' ? '2px solid #185FA5' : '2px solid transparent',
            transition: 'all 0.2s'
          }}
        >
          Upload Policies
        </div>
      </div>

      {activeTab === 'demo' ? (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 }}>
            <ScenarioCard 
              title="♿ Employee Accommodation Conflict" 
              desc="HR must provide assistive tech to employees with disabilities. IT policy bans all non-standard software. Accommodation is impossible." 
              onClick={() => onRunAnalysis("scenario_5_disability_accommodation")} 
            />
            <ScenarioCard 
              title="Analyze Entire Knowledge Base" 
              desc="Full cross-reference of all 7 policies. Azure Search + live AI reasoning." 
              onClick={() => onRunAnalysis("full_kb_analysis")} 
            />
          </div>
        </>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div 
            style={{
              border: '1px dashed #CBD5E1',
              borderRadius: 8,
              padding: 24,
              textAlign: 'center',
              background: '#F8FAFC',
              cursor: 'pointer',
              transition: 'background 0.2s'
            }}
            onClick={() => fileInputRef.current?.click()}
          >
            <input 
              type="file" 
              multiple 
              accept=".pdf,.txt,.docx,.md"
              ref={fileInputRef} 
              style={{ display: 'none' }} 
              onChange={handleFileChange}
            />
            <div style={{ fontSize: 24, marginBottom: 8 }}>📁</div>
            <div style={{ fontSize: 14, fontWeight: 500, color: '#334155' }}>
              Click to upload files
            </div>
            <div style={{ fontSize: 12, color: '#64748B', marginTop: 4 }}>
              Supports PDF, DOCX, TXT
            </div>
          </div>
          
          {files.length > 0 && (
            <div style={{ fontSize: 12, color: '#475569' }}>
              <strong>Selected ({files.length}):</strong> {files.map(f => f.name).join(', ')}
            </div>
          )}

          <button 
            onClick={handleUploadAndAnalyze}
            disabled={files.length === 0 || isUploading}
            style={{
              background: files.length === 0 || isUploading ? '#E2E8F0' : '#185FA5',
              color: files.length === 0 || isUploading ? '#94A3B8' : '#FFFFFF',
              border: 'none',
              borderRadius: 6,
              padding: '10px 16px',
              fontSize: 13,
              fontWeight: 600,
              cursor: files.length === 0 || isUploading ? 'not-allowed' : 'pointer',
              alignSelf: 'flex-start',
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              gap: 8
            }}
          >
            {isUploading ? 'Uploading & Analyzing...' : 'Analyze Conflict'}
          </button>
        </div>
      )}
    </div>
  );
}

function ScenarioCard({ title, desc, onClick }) {
  const [hover, setHover] = React.useState(false);
  return (
    <div 
      onClick={onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        background: hover ? '#F8FAFC' : '#FFFFFF',
        border: `1px solid ${hover ? '#CBD5E1' : '#E2E8F0'}`,
        borderRadius: 8,
        padding: '12px 14px',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        display: 'flex',
        flexDirection: 'column',
        gap: 6,
        boxShadow: hover ? '0 2px 4px rgba(0,0,0,0.02)' : 'none',
      }}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === 'Enter') onClick(); }}
      aria-label={`Run scenario: ${title}`}
    >
      <div style={{
        fontSize: 13,
        color: '#0F172A',
        fontWeight: 600,
      }}>
        {title}
      </div>
      <div style={{
        fontSize: 11,
        color: '#64748B',
        lineHeight: 1.4
      }}>
        {desc}
      </div>
      <div style={{
        marginTop: 'auto',
        fontSize: 11,
        color: '#2563EB',
        fontWeight: 600,
        display: 'flex',
        alignItems: 'center',
        gap: 4
      }}>
        Run Analysis ➔
      </div>
    </div>
  );
}
