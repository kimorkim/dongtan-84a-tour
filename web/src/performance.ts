const PIXEL_RATIO_STEPS = [2, 1.75, 1.5, 1.25, 1];
const SAMPLE_WINDOW = 30;
const SLOW_FRAME_MS = 26;
const FAST_FRAME_MS = 13;
const MAX_RENDER_FRAME_MS = 100;

/** Frame-rate driven pixel-ratio control with hysteresis in both directions. */
export class AdaptivePixelRatio {
  readonly levels: number[];
  private index: number;
  private samples: number[] = [];
  private fastWindows = 0;

  constructor(maximum: number, minimum = 1) {
    const max = Number.isFinite(maximum) && maximum > 0 ? maximum : 1;
    const min = Math.min(max, Number.isFinite(minimum) && minimum > 0 ? minimum : 1);
    const levels = PIXEL_RATIO_STEPS.filter((value) => value <= max + 1e-9 && value >= min - 1e-9);
    if (!levels.some((value) => Math.abs(value - max) < 1e-9)) levels.unshift(max);
    if (!levels.some((value) => Math.abs(value - min) < 1e-9)) levels.push(min);
    levels.sort((a, b) => b - a);
    this.levels = [...new Set(levels)];
    const initial = this.levels.find((value) => value <= 1.5 + 1e-9) ?? this.levels[0];
    this.index = this.levels.indexOf(initial);
  }

  get value(): number {
    return this.levels[this.index];
  }

  /** Returns the new ratio only when a step is applied. */
  observe(frameMs: number): number | null {
    if (!Number.isFinite(frameMs) || frameMs <= 0 || frameMs > MAX_RENDER_FRAME_MS) return null;
    this.samples.push(frameMs);
    if (this.samples.length < SAMPLE_WINDOW) return null;

    const sorted = [...this.samples].sort((a, b) => a - b);
    const p95 = sorted[Math.floor((sorted.length - 1) * 0.95)];
    this.samples = [];

    if (p95 > SLOW_FRAME_MS) {
      this.fastWindows = 0;
      if (this.index >= this.levels.length - 1) return null;
      this.index++;
      return this.value;
    }
    if (p95 < FAST_FRAME_MS) {
      this.fastWindows++;
      if (this.fastWindows < 2 || this.index <= 0) return null;
      this.fastWindows = 0;
      this.index--;
      return this.value;
    }
    this.fastWindows = 0;
    return null;
  }
}

export function aoUpdateInterval(pixelRatio: number): number {
  return pixelRatio <= 1.25 + 1e-9 ? 3 : 2;
}

/** Reuses the last GTAO result on alternate frames while the camera moves. */
export class AOFrameScheduler {
  private framesSinceUpdate = 0;
  private forced = true;

  forceUpdate(): void {
    this.forced = true;
  }

  shouldUpdate(moving: boolean, pixelRatio: number): boolean {
    if (this.forced || !moving) {
      this.forced = false;
      this.framesSinceUpdate = 0;
      return true;
    }
    this.framesSinceUpdate++;
    if (this.framesSinceUpdate < aoUpdateInterval(pixelRatio)) return false;
    this.framesSinceUpdate = 0;
    return true;
  }
}
