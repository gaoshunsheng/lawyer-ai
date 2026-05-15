"use client";

import { useState } from "react";
import { api } from "@/lib/api-client";
import { GANTT_NODE_TYPES } from "@/lib/constants";
import type { GanttData, GanttNode } from "@/types";

interface GanttChartProps {
  data: GanttData;
  caseId: string;
  token: string;
}

const COLOR_MAP: Record<string, string> = {
  red: "bg-red-500",
  blue: "bg-blue-500",
  green: "bg-green-500",
  purple: "bg-purple-500",
};

const COLOR_BORDER_MAP: Record<string, string> = {
  red: "border-red-500",
  blue: "border-blue-500",
  green: "border-green-500",
  purple: "border-purple-500",
};

const COLOR_BG_LIGHT: Record<string, string> = {
  red: "bg-red-100",
  blue: "bg-blue-100",
  green: "bg-green-100",
  purple: "bg-purple-100",
};

const COLOR_TEXT: Record<string, string> = {
  red: "text-red-700",
  blue: "text-blue-700",
  green: "text-green-700",
  purple: "text-purple-700",
};

function parseDate(d: string): number {
  return new Date(d).getTime();
}

function formatDate(d: string): string {
  return new Date(d).toLocaleDateString("zh-CN", { month: "2-digit", day: "2-digit" });
}

function formatDateFull(d: string): string {
  return new Date(d).toLocaleDateString("zh-CN");
}

function daysBetween(a: number, b: number): number {
  return Math.ceil((b - a) / (1000 * 60 * 60 * 24));
}

function addDays(ts: number, days: number): number {
  return ts + days * 1000 * 60 * 60 * 24;
}

export default function GanttChart({ data, caseId, token }: GanttChartProps) {
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState<string | null>(null);

  const { nodes, dependencies } = data;

  if (nodes.length === 0) {
    return (
      <div className="rounded-lg border p-8 text-center text-muted-foreground">
        暂无甘特图数据
      </div>
    );
  }

  // Calculate date range
  const starts = nodes.map((n) => parseDate(n.start));
  const ends = nodes.map((n) => parseDate(n.end));
  const minDate = Math.min(...starts);
  const maxDate = Math.max(...ends);
  const totalDays = daysBetween(minDate, maxDate) || 1;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const todayTs = today.getTime();

  // Timeline columns: show month markers
  const monthMarkers: { label: string; offset: number }[] = [];
  const cursor = new Date(minDate);
  cursor.setDate(1);
  cursor.setHours(0, 0, 0, 0);
  if (cursor.getTime() < minDate) {
    cursor.setMonth(cursor.getMonth() + 1);
  }
  while (cursor.getTime() <= maxDate) {
    const offset = daysBetween(minDate, cursor.getTime()) / totalDays * 100;
    monthMarkers.push({
      label: `${cursor.getFullYear()}-${String(cursor.getMonth() + 1).padStart(2, "0")}`,
      offset,
    });
    cursor.setMonth(cursor.getMonth() + 1);
  }

  const todayOffset = ((todayTs - minDate) / (maxDate - minDate)) * 100;

  const getColor = (node: GanttNode): string => {
    const typeInfo = GANTT_NODE_TYPES[node.type];
    return typeInfo?.color || node.color || "blue";
  };

  const isOverdue = (node: GanttNode): boolean => {
    return parseDate(node.end) < todayTs && node.status !== "completed";
  };

  // Build a row-index map for dependency SVG arrows
  const rowIndex: Record<string, number> = {};
  nodes.forEach((n, i) => {
    rowIndex[n.id] = i;
  });

  // SVG arrow paths for dependencies
  const ROW_HEIGHT = 44;
  const LEFT_WIDTH = 220;
  const BAR_AREA_WIDTH = 700;

  const depPaths = dependencies
    .map((dep) => {
      const fromIdx = rowIndex[dep.from];
      const toIdx = rowIndex[dep.to];
      const fromNode = nodes.find((n) => n.id === dep.from);
      const toNode = nodes.find((n) => n.id === dep.to);
      if (fromIdx === undefined || toIdx === undefined || !fromNode || !toNode) return null;

      const fromEnd = ((parseDate(fromNode.end) - minDate) / (maxDate - minDate)) * BAR_AREA_WIDTH;
      const toStart = ((parseDate(toNode.start) - minDate) / (maxDate - minDate)) * BAR_AREA_WIDTH;

      const x1 = LEFT_WIDTH + fromEnd;
      const y1 = fromIdx * ROW_HEIGHT + ROW_HEIGHT / 2;
      const x2 = LEFT_WIDTH + toStart;
      const y2 = toIdx * ROW_HEIGHT + ROW_HEIGHT / 2;

      const midX = x1 + (x2 - x1) / 2;
      const path = `M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`;

      return (
        <path
          key={`${dep.from}-${dep.to}`}
          d={path}
          fill="none"
          stroke="#94a3b8"
          strokeWidth="1.5"
          strokeDasharray="4 2"
          markerEnd="url(#arrowhead)"
        />
      );
    })
    .filter(Boolean);

  const svgWidth = LEFT_WIDTH + BAR_AREA_WIDTH;
  const svgHeight = nodes.length * ROW_HEIGHT;

  const handleSave = async () => {
    setSaving(true);
    setSaveMsg(null);
    try {
      await api.put(`/cases/${caseId}/gantt`, { nodes, dependencies }, token);
      setSaveMsg("保存成功");
      setTimeout(() => setSaveMsg(null), 3000);
    } catch {
      setSaveMsg("保存失败");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Action bar */}
      <div className="flex items-center gap-3">
        <button
          onClick={handleSave}
          disabled={saving}
          className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {saving ? "保存中..." : "保存甘特图"}
        </button>
        {saveMsg && (
          <span className={`text-sm ${saveMsg === "保存成功" ? "text-green-600" : "text-red-600"}`}>
            {saveMsg}
          </span>
        )}
      </div>

      {/* Chart container */}
      <div className="rounded-lg border overflow-auto">
        <div className="relative" style={{ minWidth: svgWidth }}>
          {/* Header: month markers */}
          <div className="flex border-b bg-muted/30">
            <div className="shrink-0 border-r p-2 text-xs font-medium text-muted-foreground" style={{ width: LEFT_WIDTH }}>
              任务名称
            </div>
            <div className="relative" style={{ width: BAR_AREA_WIDTH, height: 32 }}>
              {monthMarkers.map((m, i) => (
                <div
                  key={i}
                  className="absolute top-0 bottom-0 border-l text-xs text-muted-foreground flex items-end pb-1 pl-1"
                  style={{ left: `${m.offset}%` }}
                >
                  {m.label}
                </div>
              ))}
              {/* Today marker in header */}
              {todayOffset >= 0 && todayOffset <= 100 && (
                <div
                  className="absolute top-0 bottom-0 w-0.5 bg-red-400 z-10"
                  style={{ left: `${todayOffset}%` }}
                />
              )}
            </div>
          </div>

          {/* Rows */}
          {nodes.map((node, idx) => {
            const color = getColor(node);
            const startTs = parseDate(node.start);
            const endTs = parseDate(node.end);
            const leftPct = ((startTs - minDate) / (maxDate - minDate)) * 100;
            const widthPct = ((endTs - startTs) / (maxDate - minDate)) * 100;
            const overdue = isOverdue(node);
            const barColor = COLOR_MAP[color] || "bg-blue-500";
            const barBorder = COLOR_BORDER_MAP[color] || "border-blue-500";
            const bgLight = COLOR_BG_LIGHT[color] || "bg-blue-100";
            const textColor = COLOR_TEXT[color] || "text-blue-700";
            const typeLabel = GANTT_NODE_TYPES[node.type]?.label || node.type;
            const durationDays = daysBetween(startTs, endTs);

            return (
              <div
                key={node.id}
                className={`flex border-b last:border-0 ${overdue ? "bg-red-50/50" : ""}`}
                style={{ height: ROW_HEIGHT }}
              >
                {/* Left: task label */}
                <div className="shrink-0 border-r flex items-center px-3 gap-2" style={{ width: LEFT_WIDTH }}>
                  <span className={`inline-block w-2.5 h-2.5 rounded-sm shrink-0 ${barColor}`} />
                  <span className="text-sm truncate flex-1" title={node.title}>
                    {node.title}
                  </span>
                  <span className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] font-medium ${bgLight} ${textColor}`}>
                    {typeLabel}
                  </span>
                </div>

                {/* Right: bar area */}
                <div className="relative flex-1">
                  {/* Bar */}
                  <div
                    className={`absolute top-1/2 -translate-y-1/2 rounded h-6 flex items-center px-2 text-xs text-white font-medium cursor-default group ${barColor} ${overdue ? `ring-2 ring-red-500 ${barBorder}` : ""}`}
                    style={{
                      left: `${leftPct}%`,
                      width: `${Math.max(widthPct, 1)}%`,
                    }}
                  >
                    {widthPct > 8 && durationDays > 0 && (
                      <span className="truncate">{durationDays}天</span>
                    )}

                    {/* Status indicator */}
                    {node.status === "completed" && (
                      <span className="ml-1 text-white/80">&#10003;</span>
                    )}

                    {/* Tooltip */}
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-20 w-48">
                      <div className="rounded-lg bg-gray-900 text-white text-xs p-3 shadow-lg">
                        <p className="font-semibold mb-1">{node.title}</p>
                        <p className="text-gray-300">{typeLabel}</p>
                        <p className="text-gray-300">开始：{formatDateFull(node.start)}</p>
                        <p className="text-gray-300">结束：{formatDateFull(node.end)}</p>
                        <p className="text-gray-300">工期：{durationDays}天</p>
                        {node.status && (
                          <p className="text-gray-300">
                            状态：{node.status === "completed" ? "已完成" : node.status === "in_progress" ? "进行中" : node.status === "pending" ? "待开始" : node.status}
                          </p>
                        )}
                        {node.progress != null && (
                          <p className="text-gray-300">进度：{node.progress}%</p>
                        )}
                        {overdue && (
                          <p className="text-red-400 font-medium">已逾期</p>
                        )}
                      </div>
                      <div className="w-2 h-2 bg-gray-900 rotate-45 mx-auto -mt-1" />
                    </div>
                  </div>
                </div>
              </div>
            );
          })}

          {/* Today line */}
          {todayOffset >= 0 && todayOffset <= 100 && (
            <div
              className="absolute top-8 bottom-0 w-0.5 bg-red-400 z-10 pointer-events-none"
              style={{ left: LEFT_WIDTH + (todayOffset / 100) * BAR_AREA_WIDTH }}
            />
          )}

          {/* Dependency arrows (SVG overlay) */}
          {depPaths.length > 0 && (
            <svg
              className="absolute top-8 left-0 pointer-events-none z-5"
              width={svgWidth}
              height={svgHeight}
              style={{ overflow: "visible" }}
            >
              <defs>
                <marker
                  id="arrowhead"
                  markerWidth="8"
                  markerHeight="6"
                  refX="8"
                  refY="3"
                  orient="auto"
                >
                  <polygon points="0 0, 8 3, 0 6" fill="#94a3b8" />
                </marker>
              </defs>
              {depPaths}
            </svg>
          )}
        </div>
      </div>

      {/* Legend */}
      <div className="rounded-lg border p-4">
        <p className="text-sm font-medium mb-2">图例</p>
        <div className="flex flex-wrap gap-4">
          {Object.entries(GANTT_NODE_TYPES).map(([key, { label, color }]) => (
            <div key={key} className="flex items-center gap-2">
              <span className={`inline-block w-4 h-3 rounded-sm ${COLOR_MAP[color]}`} />
              <span className="text-sm text-muted-foreground">{label}</span>
            </div>
          ))}
          <div className="flex items-center gap-2">
            <span className="inline-block w-4 h-3 rounded-sm border-2 border-red-500 bg-red-50" />
            <span className="text-sm text-muted-foreground">已逾期</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block w-4 h-0.5 bg-red-400" />
            <span className="text-sm text-muted-foreground">今天</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block w-4 h-0 border-t-2 border-dashed border-gray-400" />
            <span className="text-sm text-muted-foreground">依赖关系</span>
          </div>
        </div>
      </div>
    </div>
  );
}
