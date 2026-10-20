import { GALLERY_ITEMS, type GalleryItem } from './gallery-data';

export class GalleryModal {
  private readonly modalEl: HTMLElement;
  private readonly backdropEl: HTMLElement;
  private readonly closeBtn: HTMLButtonElement;
  private readonly prevBtn: HTMLButtonElement;
  private readonly nextBtn: HTMLButtonElement;
  private readonly tabsContainer: HTMLElement;
  private readonly thumbsContainer: HTMLElement;
  private readonly imgEl: HTMLImageElement;
  private readonly titleEl: HTMLElement;
  private readonly descEl: HTMLElement;
  private readonly stageEl: HTMLElement;

  private currentCategory: string = '전체';
  private currentIndex: number = 0;
  private filteredItems: GalleryItem[] = [];
  private readonly onToggle?: (open: boolean) => void;

  private touchStartX: number = 0;
  private touchStartY: number = 0;
  private isSwiping: boolean = false;

  constructor(onToggle?: (open: boolean) => void) {
    this.onToggle = onToggle;

    this.modalEl = this.query<HTMLElement>('#gallery-modal');
    this.backdropEl = this.query<HTMLElement>('.gallery-backdrop', this.modalEl);
    this.closeBtn = this.query<HTMLButtonElement>('#btn-gallery-close', this.modalEl);
    this.prevBtn = this.query<HTMLButtonElement>('#btn-gallery-prev', this.modalEl);
    this.nextBtn = this.query<HTMLButtonElement>('#btn-gallery-next', this.modalEl);
    this.tabsContainer = this.query<HTMLElement>('#gallery-tabs', this.modalEl);
    this.thumbsContainer = this.query<HTMLElement>('#gallery-thumbs', this.modalEl);
    this.imgEl = this.query<HTMLImageElement>('#gallery-img', this.modalEl);
    this.titleEl = this.query<HTMLElement>('#gallery-title', this.modalEl);
    this.descEl = this.query<HTMLElement>('#gallery-desc', this.modalEl);
    this.stageEl = this.query<HTMLElement>('.gallery-stage', this.modalEl);

    this.filteredItems = this.getFilteredItems(this.currentCategory);

    this.bindEvents();
  }

  private query<T extends HTMLElement>(selector: string, parent: ParentNode = document): T {
    const el = parent.querySelector(selector);
    if (!el) {
      throw new Error(`GalleryModal: Element not found for selector "${selector}"`);
    }
    return el as T;
  }

  private bindEvents(): void {
    this.closeBtn.addEventListener('click', () => this.close());
    this.backdropEl.addEventListener('click', () => this.close());

    this.prevBtn.addEventListener('click', () => this.prev());
    this.nextBtn.addEventListener('click', () => this.next());

    // Tabs filtering
    this.tabsContainer.addEventListener('click', (e: MouseEvent) => {
      const target = (e.target as HTMLElement).closest<HTMLButtonElement>('.gallery-tab');
      if (!target) return;
      const room = target.dataset.room;
      if (room && room !== this.currentCategory) {
        this.setCategory(room);
      }
    });

    // Keyboard shortcuts
    window.addEventListener('keydown', (e: KeyboardEvent) => {
      if (this.modalEl.hidden) return;

      if (e.key === 'Escape') {
        e.preventDefault();
        e.stopPropagation();
        this.close();
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        e.stopPropagation();
        this.prev();
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        e.stopPropagation();
        this.next();
      }
    });

    // Touch swipe navigation on stage
    this.stageEl.addEventListener(
      'touchstart',
      (e: TouchEvent) => {
        if (e.touches.length === 1) {
          this.touchStartX = e.touches[0].clientX;
          this.touchStartY = e.touches[0].clientY;
          this.isSwiping = true;
        }
      },
      { passive: true },
    );

    this.stageEl.addEventListener(
      'touchend',
      (e: TouchEvent) => {
        if (!this.isSwiping) return;
        this.isSwiping = false;

        const touch = e.changedTouches[0];
        if (!touch) return;

        const deltaX = touch.clientX - this.touchStartX;
        const deltaY = touch.clientY - this.touchStartY;

        // Threshold: at least 40px movement and predominantly horizontal
        if (Math.abs(deltaX) > 40 && Math.abs(deltaX) > Math.abs(deltaY) * 1.2) {
          if (deltaX > 0) {
            this.prev();
          } else {
            this.next();
          }
        }
      },
      { passive: true },
    );
  }

  private getFilteredItems(category: string): GalleryItem[] {
    if (category === '전체') {
      return GALLERY_ITEMS;
    }
    if (category === '안방') {
      return GALLERY_ITEMS.filter((item) => item.room === '안방' || item.room === '발코니');
    }
    return GALLERY_ITEMS.filter((item) => item.room === category);
  }

  private getCategoryForItem(item: GalleryItem): string {
    if (item.room === '발코니') {
      return '안방';
    }
    if (item.room === '전체') {
      return '전체';
    }
    return item.room;
  }

  public setCategory(category: string): void {
    this.currentCategory = category;
    this.filteredItems = this.getFilteredItems(category);
    this.currentIndex = 0;

    this.updateTabButtons();
    this.renderThumbs();
    this.renderStage();
  }

  private updateTabButtons(): void {
    const tabBtns = this.tabsContainer.querySelectorAll<HTMLButtonElement>('.gallery-tab');
    tabBtns.forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.room === this.currentCategory);
    });
  }

  public prev(): void {
    if (this.filteredItems.length <= 1) return;
    this.currentIndex = (this.currentIndex - 1 + this.filteredItems.length) % this.filteredItems.length;
    this.renderStage();
  }

  public next(): void {
    if (this.filteredItems.length <= 1) return;
    this.currentIndex = (this.currentIndex + 1) % this.filteredItems.length;
    this.renderStage();
  }

  private renderStage(): void {
    const item = this.filteredItems[this.currentIndex];
    if (!item) return;

    this.imgEl.src = item.src;
    this.imgEl.alt = item.title;
    this.titleEl.textContent = item.title;
    this.descEl.textContent = item.description;

    // Update active state in thumbnail strip and scroll into view
    const thumbBtns = this.thumbsContainer.querySelectorAll<HTMLButtonElement>('.gallery-thumb');
    thumbBtns.forEach((btn, idx) => {
      const isActive = idx === this.currentIndex;
      btn.classList.toggle('active', isActive);
      if (isActive) {
        btn.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      }
    });
  }

  private renderThumbs(): void {
    this.thumbsContainer.innerHTML = '';
    this.filteredItems.forEach((item, idx) => {
      const btn = document.createElement('button');
      btn.className = `gallery-thumb${idx === this.currentIndex ? ' active' : ''}`;
      btn.type = 'button';
      btn.dataset.index = String(idx);
      btn.dataset.id = item.id;
      btn.setAttribute('aria-label', item.title);

      const img = document.createElement('img');
      img.src = item.thumb;
      img.alt = item.title;
      img.loading = 'lazy';

      btn.appendChild(img);
      btn.addEventListener('click', () => {
        this.currentIndex = idx;
        this.renderStage();
      });

      this.thumbsContainer.appendChild(btn);
    });
  }

  public open(itemId?: string): void {
    if (itemId) {
      const targetItem = GALLERY_ITEMS.find((it) => it.id === itemId);
      if (targetItem) {
        // If target item is already in current filtered list, keep current category
        const inCurrent = this.filteredItems.findIndex((it) => it.id === targetItem.id);
        if (inCurrent !== -1) {
          this.currentIndex = inCurrent;
        } else {
          // Switch to item's category
          this.currentCategory = this.getCategoryForItem(targetItem);
          this.filteredItems = this.getFilteredItems(this.currentCategory);
          const foundIndex = this.filteredItems.findIndex((it) => it.id === targetItem.id);
          this.currentIndex = foundIndex !== -1 ? foundIndex : 0;
        }
      }
    } else {
      if (this.filteredItems.length === 0) {
        this.filteredItems = this.getFilteredItems(this.currentCategory);
      }
      if (this.currentIndex < 0 || this.currentIndex >= this.filteredItems.length) {
        this.currentIndex = 0;
      }
    }

    this.modalEl.hidden = false;
    this.updateTabButtons();
    this.renderThumbs();
    this.renderStage();

    this.onToggle?.(true);
  }

  public close(): void {
    if (this.modalEl.hidden) return;
    this.modalEl.hidden = true;
    this.onToggle?.(false);
  }

  public isOpen(): boolean {
    return !this.modalEl.hidden;
  }
}
