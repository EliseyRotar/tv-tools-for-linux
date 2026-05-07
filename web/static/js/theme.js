class ThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'dark';
        this.themeToggle = null;
        this.themeIcon = null;
    }
    
    init() {
        this.themeToggle = document.getElementById('themeToggle');
        this.themeIcon = document.getElementById('themeIcon');
        
        if (this.themeToggle) {
            this.themeToggle.addEventListener('click', () => this.toggle());
        }
        
        this.apply(this.currentTheme);
    }
    
    toggle() {
        this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.apply(this.currentTheme);
    }
    
    apply(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        if (this.themeIcon) {
            if (theme === 'dark') {
                this.themeIcon.className = 'bi bi-sun-fill';
            } else {
                this.themeIcon.className = 'bi bi-moon-fill';
            }
        }
    }
    
    getTheme() {
        return this.currentTheme;
    }
}

const themeManager = new ThemeManager();
document.addEventListener('DOMContentLoaded', () => {
    themeManager.init();
});
