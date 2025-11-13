"use client";
import { useState } from "react";

// NEW VIBE SYSTEM - Placeholder page
// This will be replaced with the 3-question vibe flow

export default function Home() {
  return (
    <main style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      background: '#0a0a0a',
      color: '#ffffff',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <div style={{ 
        maxWidth: '600px', 
        padding: '40px', 
        textAlign: 'center' 
      }}>
        <h1 style={{ 
          fontSize: '48px', 
          fontWeight: 'bold', 
          marginBottom: '24px' 
        }}>
          VibeCheck
        </h1>
        
        <p style={{ 
          fontSize: '18px', 
          color: '#888888', 
          marginBottom: '32px' 
        }}>
          Building something that truly understands your vibe...
        </p>
        
        <div style={{
          background: '#1a1a1a',
          padding: '24px',
          borderRadius: '12px',
          textAlign: 'left'
        }}>
          <h2 style={{ 
            fontSize: '20px', 
            marginBottom: '16px' 
          }}>
            🚧 In Development
          </h2>
          
          <p style={{ 
            color: '#888888', 
            lineHeight: '1.6',
            marginBottom: '16px'
          }}>
            We're building a vibe understanding system that captures emotional complexity, 
            metaphors, and cultural context - not just keyword matching.
          </p>
          
          <p style={{ 
            color: '#888888', 
            lineHeight: '1.6' 
          }}>
            Current progress:
          </p>
          
          <ul style={{ 
            color: '#888888', 
            lineHeight: '1.8',
            marginTop: '12px',
            paddingLeft: '20px'
          }}>
            <li>✅ Reddit data collection (209 posts, 763 vibe descriptions)</li>
            <li>🔄 YouTube comment scraping (in progress)</li>
            <li>📋 Spotify playlist analysis (planned)</li>
            <li>🧠 Claude fine-tuning for vibe understanding (planned)</li>
            <li>🎨 3-question UI flow (planned)</li>
          </ul>
        </div>
        
        <p style={{ 
          marginTop: '32px',
          fontSize: '14px',
          color: '#666666'
        }}>
          Check back soon for the real magic ✨
        </p>
      </div>
    </main>
  );
}
