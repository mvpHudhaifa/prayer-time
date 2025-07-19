import streamlit as st
import requests
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="Islamic Prayer Times",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Simple CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 20px;
        background-color: #2c3e50;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
    }
    
    .section {
        background-color: #34495e;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        color: white;
    }
    
    .next-prayer {
        background-color: #3498db;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
    }
    
    .prayer-time {
        font-size: 24px;
        font-weight: bold;
        color: #f39c12;
    }
    
    .prayer-list {
        background-color: #34495e;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        color: white;
    }
    
    .prayer-row {
        display: flex;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid #4a5568;
    }
    
    .prayer-row:last-child {
        border-bottom: none;
    }
    
    .prayer-row strong {
        color: #f39c12;
    }
    
    .prayer-row small {
        color: #bdc3c7;
    }
    
    .current-time-container {
        text-align: center;
        padding: 15px;
        background-color: #34495e;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
    }
    
    .current-time {
        font-size: 2rem;
        font-weight: bold;
        color: #f39c12;
    }
</style>
""", unsafe_allow_html=True)

# Chinese cities organized by provinces
PROVINCES_CITIES = {
    "Beijing (北京)": {
        "Beijing (北京)": {"lat": 39.9042, "lng": 116.4074}
    },
    "Shanghai (上海)": {
        "Shanghai (上海)": {"lat": 31.2304, "lng": 121.4737}
    },
    "Tianjin (天津)": {
        "Tianjin (天津)": {"lat": 39.3434, "lng": 117.3616}
    },
    "Chongqing (重庆)": {
        "Chongqing (重庆)": {"lat": 29.4316, "lng": 106.9123}
    },
    "Guangdong (广东)": {
        "Guangzhou (广州)": {"lat": 23.1291, "lng": 113.2644},
        "Shenzhen (深圳)": {"lat": 22.3193, "lng": 114.1694},
        "Dongguan (东莞)": {"lat": 23.0207, "lng": 113.7518},
        "Foshan (佛山)": {"lat": 23.0218, "lng": 113.1219},
        "Zhuhai (珠海)": {"lat": 22.2707, "lng": 113.5767},
        "Shantou (汕头)": {"lat": 23.3541, "lng": 116.6820},
        "Huizhou (惠州)": {"lat": 23.1116, "lng": 114.4162},
        "Zhongshan (中山)": {"lat": 22.5176, "lng": 113.3928},
        "Jiangmen (江门)": {"lat": 22.5787, "lng": 113.0819},
        "Zhaoqing (肇庆)": {"lat": 23.0471, "lng": 112.4651},
        "Qingyuan (清远)": {"lat": 23.6820, "lng": 113.0560},
        "Shaoguan (韶关)": {"lat": 24.8108, "lng": 113.5972},
        "Meizhou (梅州)": {"lat": 24.2886, "lng": 116.1222},
        "Chaozhou (潮州)": {"lat": 23.6571, "lng": 116.6226},
        "Jieyang (揭阳)": {"lat": 23.5498, "lng": 116.3728},
        "Yunfu (云浮)": {"lat": 22.9150, "lng": 112.0444},
        "Yangjiang (阳江)": {"lat": 21.8579, "lng": 111.9822},
        "Maoming (茂名)": {"lat": 21.6630, "lng": 110.9254},
        "Zhanjiang (湛江)": {"lat": 21.2707, "lng": 110.3594}
    },
    "Zhejiang (浙江)": {
        "Hangzhou (杭州)": {"lat": 30.2741, "lng": 120.1551},
        "Ningbo (宁波)": {"lat": 29.8683, "lng": 121.5440},
        "Wuxi (无锡)": {"lat": 31.4900, "lng": 120.3119},
        "Suzhou (苏州)": {"lat": 31.2990, "lng": 120.5853},
        "Jinhua (金华)": {"lat": 29.0784, "lng": 119.6474},
        "Shaoxing (绍兴)": {"lat": 30.0297, "lng": 120.5853},
        "Taizhou (台州)": {"lat": 28.6560, "lng": 121.4206},
        "Wenzhou (温州)": {"lat": 27.9938, "lng": 120.6990}
    },
    "Jiangsu (江苏)": {
        "Nanjing (南京)": {"lat": 32.0603, "lng": 118.7969},
        "Yangzhou (扬州)": {"lat": 32.3945, "lng": 119.4129},
        "Huangshan (黄山)": {"lat": 29.7147, "lng": 118.3376},
        "Chizhou (池州)": {"lat": 30.6648, "lng": 117.4914},
        "Xuancheng (宣城)": {"lat": 30.9454, "lng": 118.7587},
        "Lu'an (六安)": {"lat": 31.7337, "lng": 116.5224},
        "Bozhou (亳州)": {"lat": 33.8712, "lng": 115.7787},
        "Chuzhou (滁州)": {"lat": 32.3019, "lng": 118.3218},
        "Fuyang (阜阳)": {"lat": 32.8897, "lng": 115.8142},
        "Suzhou (宿州)": {"lat": 33.6462, "lng": 116.9641},
        "Huaibei (淮北)": {"lat": 33.9544, "lng": 116.7983},
        "Huainan (淮南)": {"lat": 32.6255, "lng": 116.9998},
        "Bengbu (蚌埠)": {"lat": 32.9164, "lng": 117.3889},
        "Anqing (安庆)": {"lat": 30.5433, "lng": 117.0634},
        "Tongling (铜陵)": {"lat": 30.9454, "lng": 117.8121},
        "Ma'anshan (马鞍山)": {"lat": 31.6702, "lng": 118.5061},
        "Wuhu (芜湖)": {"lat": 31.3529, "lng": 118.4331}
    },
    "Hubei (湖北)": {
        "Wuhan (武汉)": {"lat": 30.5928, "lng": 114.3055}
    },
    "Sichuan (四川)": {
        "Chengdu (成都)": {"lat": 30.5728, "lng": 104.0668}
    },
    "Shaanxi (陕西)": {
        "Xi'an (西安)": {"lat": 34.3416, "lng": 108.9398}
    },
    "Shandong (山东)": {
        "Qingdao (青岛)": {"lat": 36.0671, "lng": 120.3826},
        "Jinan (济南)": {"lat": 36.6510, "lng": 117.1201}
    },
    "Liaoning (辽宁)": {
        "Dalian (大连)": {"lat": 38.9140, "lng": 121.6147},
        "Shenyang (沈阳)": {"lat": 41.8057, "lng": 123.4315}
    },
    "Fujian (福建)": {
        "Xiamen (厦门)": {"lat": 24.4798, "lng": 118.0894},
        "Fuzhou (福州)": {"lat": 26.0745, "lng": 119.2965}
    },
    "Yunnan (云南)": {
        "Kunming (昆明)": {"lat": 25.0389, "lng": 102.7183}
    },
    "Heilongjiang (黑龙江)": {
        "Harbin (哈尔滨)": {"lat": 45.8030, "lng": 126.5349}
    },
    "Jilin (吉林)": {
        "Changchun (长春)": {"lat": 43.8171, "lng": 125.3239},
        "Jilin (吉林)": {"lat": 43.8378, "lng": 126.5496}
    },
    "Henan (河南)": {
        "Zhengzhou (郑州)": {"lat": 34.7472, "lng": 113.6253}
    },
    "Hebei (河北)": {
        "Shijiazhuang (石家庄)": {"lat": 38.0428, "lng": 114.5149},
        "Tangshan (唐山)": {"lat": 39.6309, "lng": 118.1804},
        "Qinhuangdao (秦皇岛)": {"lat": 39.9354, "lng": 119.6005},
        "Handan (邯郸)": {"lat": 36.6253, "lng": 114.5391},
        "Xingtai (邢台)": {"lat": 37.0682, "lng": 114.5049},
        "Baoding (保定)": {"lat": 38.8671, "lng": 115.4823},
        "Zhangjiakou (张家口)": {"lat": 40.7686, "lng": 114.8841},
        "Chengde (承德)": {"lat": 40.9515, "lng": 117.9634},
        "Langfang (廊坊)": {"lat": 39.5379, "lng": 116.6838},
        "Hengshui (衡水)": {"lat": 37.7351, "lng": 115.6702}
    },
    "Shanxi (山西)": {
        "Taiyuan (太原)": {"lat": 37.8706, "lng": 112.5489},
        "Datong (大同)": {"lat": 40.0768, "lng": 113.2982}
    },
    "Inner Mongolia (内蒙古)": {
        "Baotou (包头)": {"lat": 40.6571, "lng": 109.8403}
    },
    "Ningxia (宁夏)": {
        "Yinchuan (银川)": {"lat": 38.4872, "lng": 106.2309}
    },
    "Qinghai (青海)": {
        "Xining (西宁)": {"lat": 36.6230, "lng": 101.7803}
    },
    "Gansu (甘肃)": {
        "Lanzhou (兰州)": {"lat": 36.0611, "lng": 103.8343}
    },
    "Xinjiang (新疆)": {
        "Urumqi (乌鲁木齐)": {"lat": 43.8256, "lng": 87.6168},
        "Kashgar (喀什)": {"lat": 39.4704, "lng": 75.9897}
    },
    "Tibet (西藏)": {
        "Lhasa (拉萨)": {"lat": 29.6500, "lng": 91.1000}
    },
    "Guizhou (贵州)": {
        "Guiyang (贵阳)": {"lat": 26.6470, "lng": 106.6302}
    },
    "Guangxi (广西)": {
        "Liuzhou (柳州)": {"lat": 24.3146, "lng": 109.4283},
        "Nanning (南宁)": {"lat": 22.8170, "lng": 108.3665},
        "Beihai (北海)": {"lat": 21.4733, "lng": 109.1201},
        "Fangchenggang (防城港)": {"lat": 21.6861, "lng": 108.3538},
        "Qinzhou (钦州)": {"lat": 21.9797, "lng": 108.6242},
        "Guigang (贵港)": {"lat": 23.1115, "lng": 109.5986},
        "Yulin (玉林)": {"lat": 22.6540, "lng": 110.1804},
        "Baise (百色)": {"lat": 23.9023, "lng": 106.6186},
        "Hezhou (贺州)": {"lat": 24.4037, "lng": 111.5521},
        "Hechi (河池)": {"lat": 24.6995, "lng": 108.0621},
        "Laibin (来宾)": {"lat": 23.7507, "lng": 109.2298},
        "Chongzuo (崇左)": {"lat": 22.4041, "lng": 107.3539}
    },
    "Hainan (海南)": {
        "Haikou (海口)": {"lat": 20.0440, "lng": 110.1920},
        "Sanya (三亚)": {"lat": 18.2528, "lng": 109.5119}
    },
    "Jiangxi (江西)": {
        "Nanchang (南昌)": {"lat": 28.6820, "lng": 115.8579},
        "Jingdezhen (景德镇)": {"lat": 29.2688, "lng": 117.1789},
        "Pingxiang (萍乡)": {"lat": 27.6229, "lng": 113.8544},
        "Jiujiang (九江)": {"lat": 29.7196, "lng": 116.0019},
        "Xinyu (新余)": {"lat": 27.8174, "lng": 114.9173},
        "Yingtan (鹰潭)": {"lat": 28.2602, "lng": 117.0692},
        "Ganzhou (赣州)": {"lat": 25.8452, "lng": 114.9340},
        "Ji'an (吉安)": {"lat": 27.1138, "lng": 114.9927},
        "Yichun (宜春)": {"lat": 27.8043, "lng": 114.3917},
        "Fuzhou (抚州)": {"lat": 27.9839, "lng": 116.3584},
        "Shangrao (上饶)": {"lat": 28.4549, "lng": 117.9434}
    },
    "Hunan (湖南)": {
        "Changsha (长沙)": {"lat": 28.2278, "lng": 112.9388}
    },
    "Anhui (安徽)": {
        "Hefei (合肥)": {"lat": 31.8206, "lng": 117.2272}
    }
}

def get_prayer_times(lat, lng, date=None):
    """Fetch prayer times from Aladhan API"""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Using Aladhan API
        url = f"http://api.aladhan.com/v1/timings/{date}?latitude={lat}&longitude={lng}&method=2"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            timings = data['data']['timings']
            
            prayer_times = {
                'Fajr': timings.get('Fajr', '--:--'),
                'Sunrise': timings.get('Sunrise', '--:--'),
                'Dhuhr': timings.get('Dhuhr', '--:--'),
                'Asr': timings.get('Asr', '--:--'),
                'Maghrib': timings.get('Maghrib', '--:--'),
                'Isha': timings.get('Isha', '--:--')
            }
            
            return prayer_times
    except Exception as e:
        st.error(f"Error fetching prayer times: {str(e)}")
    
    # Fallback prayer times if API fails
    return {
        'Fajr': '--:--',
        'Sunrise': '--:--',
        'Dhuhr': '--:--',
        'Asr': '--:--',
        'Maghrib': '--:--',
        'Isha': '--:--'
    }

def get_next_prayer(prayer_times):
    """Determine the next prayer"""
    now = datetime.now()
    current_time = now.strftime('%H:%M')
    
    prayer_order = ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
    
    for prayer in prayer_order:
        if prayer in prayer_times and prayer_times[prayer] != '--:--':
            if prayer_times[prayer] > current_time:
                return prayer
    
    # If no prayer found for today, return tomorrow's Fajr
    return 'Fajr'

def format_time_difference(prayer_time):
    """Calculate time difference to next prayer"""
    now = datetime.now()
    try:
        prayer_dt = datetime.strptime(prayer_time, '%H:%M').replace(
            year=now.year, month=now.month, day=now.day
        )
        
        if prayer_dt < now:
            prayer_dt += timedelta(days=1)
        
        diff = prayer_dt - now
        hours = int(diff.total_seconds() // 3600)
        minutes = int((diff.total_seconds() % 3600) // 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    except:
        return ""

# Main app
def main():
    # Initialize session state
    if 'selected_province' not in st.session_state:
        st.session_state.selected_province = "Jiangsu (江苏)"
    if 'selected_city' not in st.session_state:
        st.session_state.selected_city = "Yangzhou (扬州)"
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = datetime.now().date()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🕌 Islamic Prayer Times</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Current time display
    current_time = datetime.now().strftime('%H:%M:%S')
    st.markdown(f"""
    <div class="current-time-container">
        <div class="current-time">🕐 {current_time}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Location selection
    with st.container():
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.subheader("📍 Select Location")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Province selection
            selected_province = st.selectbox(
                "Province:",
                list(PROVINCES_CITIES.keys()),
                index=list(PROVINCES_CITIES.keys()).index(st.session_state.selected_province),
                key="province_select"
            )
            
            if selected_province != st.session_state.selected_province:
                st.session_state.selected_province = selected_province
                # Reset city to first city in new province
                st.session_state.selected_city = list(PROVINCES_CITIES[selected_province].keys())[0]
                st.rerun()
        
        with col2:
            # City selection based on selected province
            cities_in_province = list(PROVINCES_CITIES[selected_province].keys())
            selected_city = st.selectbox(
                "City:",
                cities_in_province,
                index=cities_in_province.index(st.session_state.selected_city) if st.session_state.selected_city in cities_in_province else 0,
                key="city_select"
            )
            
            if selected_city != st.session_state.selected_city:
                st.session_state.selected_city = selected_city
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Get coordinates for selected city
    city_coords = PROVINCES_CITIES[st.session_state.selected_province][st.session_state.selected_city]
    
    # Date selection
    with st.container():
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.subheader("📅 Select Date")
        
        selected_date = st.date_input(
            "Choose date:",
            value=st.session_state.selected_date,
            key="date_picker"
        )
        
        if selected_date != st.session_state.selected_date:
            st.session_state.selected_date = selected_date
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Get prayer times
    with st.spinner('Fetching prayer times...'):
        prayer_times = get_prayer_times(city_coords['lat'], city_coords['lng'], selected_date.strftime('%Y-%m-%d'))
    
    # Next prayer
    next_prayer = get_next_prayer(prayer_times)
    next_prayer_time = prayer_times.get(next_prayer, '--:--')
    time_diff = format_time_difference(next_prayer_time)
    
    st.markdown(f"""
    <div class="next-prayer">
        <h3>🕌 Next Prayer: {next_prayer}</h3>
        <div class="prayer-time">{next_prayer_time}</div>
        <div style="color: #f39c12; font-size: 16px;">⏰ {time_diff} remaining</div>
    </div>
    """, unsafe_allow_html=True)
    
    # All prayer times
    st.markdown("""
    <div class="prayer-list">
        <h3>📋 Prayer Times for """ + selected_date.strftime('%B %d, %Y') + """</h3>
    """, unsafe_allow_html=True)
    
    # Prayer names in Arabic
    prayer_names_arabic = {
        'Fajr': 'الفجر',
        'Sunrise': 'الشروق',
        'Dhuhr': 'الظهر',
        'Asr': 'العصر',
        'Maghrib': 'المغرب',
        'Isha': 'العشاء'
    }
    
    prayers = [
        ('Fajr', '🌅'),
        ('Sunrise', '☀️'),
        ('Dhuhr', '🌞'),
        ('Asr', '🌤️'),
        ('Maghrib', '🌆'),
        ('Isha', '🌙')
    ]
    
    for prayer, emoji in prayers:
        st.markdown(f"""
        <div class="prayer-row">
            <div>
                <strong>{emoji} {prayer}</strong><br>
                <small>{prayer_names_arabic.get(prayer, '')}</small>
            </div>
            <div class="prayer-time">{prayer_times.get(prayer, '--:--')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    time.sleep(1)
    st.rerun()
if __name__ == "__main__":
    main()
