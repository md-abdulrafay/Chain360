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

        var menu,btn,overflow;
        
        item.addEventListener('click' , function(){            

            for (let i = 0; i < this.children.length; i++) {
                const e = this.children[i];

                if (e.classList.contains('menu')) {
                    menu = e;                  
                }else if (e.classList.contains('menu-btn')) {
                    btn = e;
                }else if (e.classList.contains('menu-overflow')) {
                    overflow = e;
                }
                              
            }
            
            if (menu.classList.contains('hidden')) {
                // show the menu
                showMenu();
            }else{
                // hide the menu
                hideMenu()
            }      


        });        
        

        var showMenu = function(){
            menu.classList.remove('hidden');
            menu.classList.add('fadeIn');
            overflow.classList.remove('hidden');            
        };

        var hideMenu = function(){
            menu.classList.add('hidden');
            overflow.classList.add('hidden');            
            menu.classList.remove('fadeIn');            
        };
        
                
        
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
