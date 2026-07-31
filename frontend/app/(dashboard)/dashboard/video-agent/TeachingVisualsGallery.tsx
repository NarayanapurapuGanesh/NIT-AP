"use client";

import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Download, Search, Maximize2, FileDown, Layers, Map, Calculator, TerminalSquare } from 'lucide-react';
import Image from 'next/image';

interface VisualData {
  id: number;
  filename: string;
  timestamp: string;
  timestamp_sec: number;
  ocr: string;
  keywords: string;
  topic: string;
  diagram_type: string;
  linked_transcript_id: string | null;
}

export function TeachingVisualsGallery({ jobId }: { jobId: string }) {
  const [visuals, setVisuals] = useState<VisualData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [filterTopic, setFilterTopic] = useState('All');
  const [lightboxImage, setLightboxImage] = useState<VisualData | null>(null);

  useEffect(() => {
    if (!jobId) return;
    fetch(`http://localhost:8005/video/${jobId}/visuals`)
      .then(async res => {
        if (!res.ok) {
          let errorDetail = res.statusText;
          try {
            const errData = await res.json();
            errorDetail = errData.detail || errorDetail;
          } catch (e) {
            // Ignore if parsing JSON fails
          }
          throw new Error(errorDetail);
        }
        return res.json();
      })
      .then(data => {
        setVisuals(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load visuals:", err);
        setError(err.message || "Failed to connect to the Video Agent");
        setLoading(false);
      });
  }, [jobId]);

  const topics = ['All', ...Array.from(new Set(visuals.map(v => v.topic)))];

  const filteredVisuals = visuals.filter(v => {
    const matchesSearch = v.ocr.toLowerCase().includes(search.toLowerCase()) || 
                          v.diagram_type.toLowerCase().includes(search.toLowerCase());
    const matchesTopic = filterTopic === 'All' || v.topic === filterTopic;
    return matchesSearch && matchesTopic;
  });

  const downloadPDF = () => {
    window.open(`http://localhost:8005/video/${jobId}/download/pdf`, '_blank');
  };

  const downloadZIP = () => {
    window.open(`http://localhost:8005/video/${jobId}/download/zip`, '_blank');
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading extracted visuals...</div>;
  }

  if (error) {
    return (
      <div className="p-6 bg-red-950/30 border border-red-900/50 rounded-xl text-red-400 text-sm">
        <h3 className="font-bold mb-1 text-red-300">Backend Error</h3>
        <p>{error}</p>
      </div>
    );
  }

  if (visuals.length === 0) {
    return (
      <div className="p-8 text-center text-slate-400">
        <Layers className="h-12 w-12 mx-auto mb-3 opacity-20" />
        No teaching visuals were extracted from this video.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters and Exports */}
      <div className="flex flex-col md:flex-row justify-between items-center gap-4 bg-slate-950/40 p-4 rounded-xl border border-slate-800">
        <div className="flex items-center gap-3 w-full md:w-auto">
          <div className="relative w-full md:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
            <input 
              type="text"
              placeholder="Search OCR text..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-sm text-white focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <select 
            value={filterTopic} 
            onChange={e => setFilterTopic(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:ring-1 focus:ring-indigo-500"
          >
            {topics.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
        
        <div className="flex items-center gap-2">
          <Button onClick={downloadPDF} size="sm" className="bg-rose-600/20 text-rose-400 hover:bg-rose-600/40 border border-rose-500/30">
            <FileDown className="h-4 w-4 mr-2" /> PDF Report
          </Button>
          <Button onClick={downloadZIP} size="sm" className="bg-sky-600/20 text-sky-400 hover:bg-sky-600/40 border border-sky-500/30">
            <Download className="h-4 w-4 mr-2" /> Export ZIP
          </Button>
        </div>
      </div>

      {/* Gallery Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {filteredVisuals.map((visual) => (
          <Card key={visual.id} className="bg-slate-900 border-slate-800 overflow-hidden group">
            <div className="relative aspect-video bg-black cursor-pointer" onClick={() => setLightboxImage(visual)}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img 
                src={`http://localhost:8005/video/${jobId}/visuals/${visual.id}`}
                alt={visual.diagram_type}
                className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"
              />
              <div className="absolute top-2 right-2 bg-black/60 text-white text-[10px] px-2 py-1 rounded-md backdrop-blur-md">
                {visual.timestamp}
              </div>
              <div className="absolute inset-0 bg-indigo-900/0 group-hover:bg-indigo-900/40 transition-colors flex items-center justify-center">
                <Maximize2 className="text-white opacity-0 group-hover:opacity-100 transition-opacity drop-shadow-lg" />
              </div>
            </div>
            <CardContent className="p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-indigo-400 flex items-center gap-1">
                  {visual.topic === 'Programming' && <TerminalSquare className="h-3 w-3" />}
                  {visual.topic === 'Mathematics' && <Calculator className="h-3 w-3" />}
                  {(visual.topic !== 'Programming' && visual.topic !== 'Mathematics') && <Map className="h-3 w-3" />}
                  {visual.topic}
                </span>
                <span className="text-[10px] text-slate-500 bg-slate-800 px-2 py-0.5 rounded-full">
                  {visual.diagram_type !== 'None' ? visual.diagram_type : 'Slide'}
                </span>
              </div>
              <p className="text-xs text-slate-300 line-clamp-2" title={visual.ocr}>
                {visual.ocr || <span className="text-slate-600 italic">No text detected</span>}
              </p>
              {visual.linked_transcript_id && (
                <div className="text-[10px] text-emerald-400 font-medium pt-2 border-t border-slate-800">
                  ✓ Linked to transcript segment
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Lightbox Modal */}
      {lightboxImage && (
        <div className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4 backdrop-blur-sm" onClick={() => setLightboxImage(null)}>
          <div className="max-w-5xl w-full bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl" onClick={e => e.stopPropagation()}>
            <div className="flex justify-between items-center p-4 border-b border-slate-800">
              <h3 className="text-white font-bold flex items-center gap-2">
                <span className="text-indigo-400">{lightboxImage.timestamp}</span> 
                <span>{lightboxImage.topic} - {lightboxImage.diagram_type !== 'None' ? lightboxImage.diagram_type : 'Slide'}</span>
              </h3>
              <button onClick={() => setLightboxImage(null)} className="text-slate-400 hover:text-white text-2xl leading-none">&times;</button>
            </div>
            <div className="p-4 flex flex-col md:flex-row gap-6">
              <div className="flex-1 bg-black rounded-lg overflow-hidden border border-slate-800 flex items-center justify-center">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img 
                  src={`http://localhost:8005/video/${jobId}/visuals/${lightboxImage.id}`}
                  alt="Full Visual"
                  className="max-h-[60vh] object-contain"
                />
              </div>
              <div className="w-full md:w-80 space-y-4">
                <div>
                  <h4 className="text-xs font-bold text-slate-500 uppercase mb-2">OCR Extraction</h4>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 h-48 overflow-y-auto">
                    <p className="text-xs text-slate-300 whitespace-pre-wrap">{lightboxImage.ocr || 'No text detected.'}</p>
                  </div>
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-500 uppercase mb-2">Keywords</h4>
                  <div className="flex flex-wrap gap-1">
                    {lightboxImage.keywords.split(',').filter(Boolean).map(kw => (
                      <span key={kw} className="text-[10px] bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 px-2 py-1 rounded-md">
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
