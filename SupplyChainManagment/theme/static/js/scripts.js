// Toastify Notification Helper Functions
function showToast(message, type = 'info') {
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    
    Toastify({
        text: message,
        duration: 4000,
        gravity: "top",
        position: "right",
        backgroundColor: colors[type] || colors.info,
        className: "toast-message",
        stopOnFocus: true,
        style: {
            borderRadius: "8px",
            fontWeight: "500",
            boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
        }
    }).showToast();
}

// Convenience functions
function showSuccess(message) { showToast(message, 'success'); }
function showError(message) { showToast(message, 'error'); }
function showWarning(message) { showToast(message, 'warning'); }
function showInfo(message) { showToast(message, 'info'); }

// get the close btn
var alert_button = document.getElementsByClassName("alert-btn-close");

// looping into all alert close btns
for (let i = 0; i < alert_button.length; i++) {
    const btn = alert_button[i];

    btn.addEventListener('click' , function(){
        var dad = this.parentNode;
        dad.classList.add('animated' , 'fadeOut');
        setTimeout(() => {
            dad.remove();
        }, 1000);
    });
    
}
// check if the page have dropdwon menu
var dropdown = document.getElementsByClassName('dropdown');

if (dropdown.length >= 1) {
    for (let i = 0; i < dropdown.length; i++) {
        const item = dropdown[i];
        var menu = item.querySelector('.menu');
        var btn = item.querySelector('.menu-btn');
        var overflow = item.querySelector('.menu-overflow');
        if (btn) {
            btn.addEventListener('click', function(e) {
                e.stopPropagation(); // Prevent bubbling
                if (menu && overflow) {
                    if (menu.classList.contains('hidden')) {
                        menu.classList.remove('hidden');
                        menu.classList.add('fadeIn');
                        overflow.classList.remove('hidden');
                    } else {
                        menu.classList.add('hidden');
                        overflow.classList.add('hidden');
                        menu.classList.remove('fadeIn');
                    }
                }
            });
        }
        // Optional: close dropdown if clicking outside
        document.addEventListener('click', function(e) {
            if (menu && overflow && !item.contains(e.target)) {
                menu.classList.add('hidden');
                overflow.classList.add('hidden');
                menu.classList.remove('fadeIn');
            }
        });
    }    
    
};

// --- REMOVE ALL RANDOM DATA GENERATION FOR .num-2, .num-3, .num-4, .name-1, .name-2 ---
// Removed all code that sets or overwrites .num-2, .num-3, .num-4, .name-1, .name-2 elements.
// --- END OF RANDOM DATA GENERATION REMOVAL ---

// work with sidebar
var btn     = document.getElementById('sliderBtn'),
    sideBar = document.getElementById('sideBar'),
    sideBarHideBtn = document.getElementById('sideBarHideBtn');

    // show sidebar 
    btn.addEventListener('click' , function(){    
        if (sideBar.classList.contains('md:-ml-64')) {
            sideBar.classList.replace('md:-ml-64' , 'md:ml-0');
            sideBar.classList.remove('md:slideOutLeft');
            sideBar.classList.add('md:slideInLeft');
        };
    });

    // hide sideBar    
    sideBarHideBtn.addEventListener('click' , function(){            
        if (sideBar.classList.contains('md:ml-0' , 'slideInLeft')) {      
            var _class = function(){
                sideBar.classList.remove('md:slideInLeft');
                sideBar.classList.add('md:slideOutLeft');
        
                console.log('hide');              
            };
            var animate = async function(){
                await _class();

                setTimeout(function(){
                    sideBar.classList.replace('md:ml-0' , 'md:-ml-64');
                    console.log('animated');
                } , 300);                                                
                
            };            
                    
            _class(); 
            animate();
        };
    });
// end with sidebar

// --- SALES OVERVIEW BAR CHART WITH REAL DATA ---
(function() {
    // Get product names and sales counts from the template
    var namesScript = document.getElementById('product-names-data');
    var salesScript = document.getElementById('product-sales-data');
    if (!namesScript || !salesScript) return;
    try {
        var productNames = JSON.parse(namesScript.textContent.trim());
        var salesCounts = JSON.parse(salesScript.textContent.trim());
        // Only render if both arrays are valid
        if (Array.isArray(productNames) && Array.isArray(salesCounts) && productNames.length === salesCounts.length) {
            var options = {
                chart: {
                    type: 'bar',
                    height: 350
                },
                series: [{
                    name: 'Sales',
                    data: salesCounts
                }],
                xaxis: {
                    categories: productNames
                },
                colors: ['#22c55e'], // green color
                title: {
                    text: 'Sales Overview (This Month)',
                    align: 'left',
                    style: { fontSize: '18px', fontWeight: 'bold' }
                }
            };
            var chart = new ApexCharts(document.querySelector('#productSalesApexChart'), options);
            chart.render();
        }
    } catch (e) {
        console.error('Error parsing product sales data:', e);
    }
})();
// --- END SALES OVERVIEW BAR CHART ---

// --- ANALYTICS_1 CHARTS WITH RANDOM BUT VALID DATA (following scripts copy.js) ---
(function() {
    if (typeof ApexCharts === 'undefined') return;
    var numArr = function(length, max) {
        return Array.from({length: length}, () => Math.floor(Math.random() * max));
    };
    var analytics_1 =  document.getElementsByClassName("analytics_1");
    if (analytics_1 != null && typeof(analytics_1) != 'undefined') {
        var chart = new ApexCharts(analytics_1[0], {
            chart: {
                type: 'area',
                height: '51px',
                width: '100%',
                sparkline: { enabled: true },
                toolbar: { show: false }
            },
            grid: { show: false, padding: { top: 0, right: 0, bottom: 0, left: 0 } },
            dataLabels: { enabled: false },
            legend: { show: false },
            series: [{ name: 'Page Views', data: numArr(10, 99) }],
            fill: { colors: ['#4fd1c5'] },
            stroke: { colors: ['#4fd1c5'], width: 3 },
            yaxis: { show: false },
            xaxis: { show: false, labels: { show: false }, axisBorder: { show: false }, tooltip: { enabled: false } }
        });
        var chart_1 = new ApexCharts(analytics_1[1], {
            chart: {
                type: 'area',
                height: '51px',
                width: '100%',
                sparkline: { enabled: true },
                toolbar: { show: false }
            },
            grid: { show: false, padding: { top: 0, right: 0, bottom: 0, left: 0 } },
            dataLabels: { enabled: false },
            legend: { show: false },
            series: [{ name: 'Unique Users', data: numArr(10, 99) }],
            fill: { colors: ['#4c51bf'] },
            stroke: { colors: ['#4c51bf'], width: 3 },
            yaxis: { show: false },
            xaxis: { show: false, labels: { show: false }, axisBorder: { show: false }, tooltip: { enabled: false } }
        });
        chart.render();
        chart_1.render();
    }
})();
// --- END ANALYTICS_1 CHARTS ---

// --- Improved dropdown logic: only open on button click, close on outside click ---
(function() {
    var dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(function(dropdown) {
        var btn = dropdown.querySelector('.menu-btn');
        var menu = dropdown.querySelector('.menu');
        var overflow = dropdown.querySelector('.menu-overflow');
        if (!btn || !menu || !overflow) return;
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            // Hide all other dropdowns
            document.querySelectorAll('.menu').forEach(function(m) {
                if (m !== menu) m.classList.add('hidden');
            });
            document.querySelectorAll('.menu-overflow').forEach(function(o) {
                if (o !== overflow) o.classList.add('hidden');
            });
            menu.classList.toggle('hidden');
            menu.classList.toggle('fadeIn');
            overflow.classList.toggle('hidden');
        });
        overflow.addEventListener('click', function(e) {
            menu.classList.add('hidden');
            menu.classList.remove('fadeIn');
            overflow.classList.add('hidden');
        });
        // Close dropdown if clicking outside
        document.addEventListener('click', function(e) {
            if (!dropdown.contains(e.target)) {
                menu.classList.add('hidden');
                menu.classList.remove('fadeIn');
                overflow.classList.add('hidden');
            }
        });
    });
})();
// --- END Improved dropdown logic ---
