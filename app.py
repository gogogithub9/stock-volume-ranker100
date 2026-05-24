from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import json
from models import Database, StockVolumeModel, CrawlerLogModel, DailyRankingModel
from crawler import StockCrawler
from config import FLASK_PORT, FLASK_DEBUG, SECRET_KEY, API_DEFAULT_LIMIT, API_HISTORY_DAYS
from utils.logger import get_logger

logger = get_logger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# ============ Web Routes ============

@app.route('/')
def index():
    """首页"""
    db = Database()
    db.connect()
    
    # 获取最新数据
    latest_data = StockVolumeModel.get_latest(db, API_DEFAULT_LIMIT)
    
    # 获取统计信息
    dates = StockVolumeModel.get_all_dates(db)
    
    db.disconnect()
    
    return render_template('index.html', 
                         data=latest_data, 
                         dates=[str(d[0]) for d in dates] if dates else [])

@app.route('/history')
def history():
    """历史分���页面"""
    db = Database()
    db.connect()
    
    dates = StockVolumeModel.get_all_dates(db)
    daily_stats = DailyRankingModel.get_range(db, API_HISTORY_DAYS)
    
    db.disconnect()
    
    return render_template('history.html',
                         dates=[str(d[0]) for d in dates] if dates else [],
                         stats=daily_stats)

@app.route('/api')
def api_docs():
    """API文档页面"""
    return render_template('api.html')

# ============ API Routes ============

@app.route('/api/latest', methods=['GET'])
def api_latest():
    """获取最新排名"""
    try:
        limit = request.args.get('limit', API_DEFAULT_LIMIT, type=int)
        limit = min(limit, 1000)
        
        db = Database()
        db.connect()
        data = StockVolumeModel.get_latest(db, limit)
        db.disconnect()
        
        result = []
        for row in data:
            result.append({
                'rank': row[3],
                'code': row[4],
                'name': row[5],
                'volume': row[6],
                'amount': row[7],
                'price': row[8],
                'change': row[9],
                'date': row[1],
                'time': row[2]
            })
        
        return jsonify({
            'success': True,
            'count': len(result),
            'data': result
        })
    
    except Exception as e:
        logger.error(f"API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def api_history():
    """获取历史数据"""
    try:
        date = request.args.get('date', None)
        limit = request.args.get('limit', API_DEFAULT_LIMIT, type=int)
        limit = min(limit, 1000)
        
        db = Database()
        db.connect()
        
        if date:
            data = StockVolumeModel.get_by_date(db, date, limit)
        else:
            data = StockVolumeModel.get_latest(db, limit)
        
        db.disconnect()
        
        result = []
        for row in data:
            result.append({
                'rank': row[3],
                'code': row[4],
                'name': row[5],
                'volume': row[6],
                'amount': row[7],
                'price': row[8],
                'change': row[9],
                'date': row[1],
                'time': row[2]
            })
        
        return jsonify({
            'success': True,
            'count': len(result),
            'data': result
        })
    
    except Exception as e:
        logger.error(f"API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stock/<code>', methods=['GET'])
def api_stock(code):
    """获取股票历史"""
    try:
        days = request.args.get('days', 30, type=int)
        
        db = Database()
        db.connect()
        data = StockVolumeModel.get_stock_history(db, code, days)
        db.disconnect()
        
        result = []
        for row in data:
            result.append({
                'rank': row[3],
                'code': row[4],
                'name': row[5],
                'volume': row[6],
                'amount': row[7],
                'price': row[8],
                'change': row[9],
                'date': row[1],
                'time': row[2]
            })
        
        return jsonify({
            'success': True,
            'count': len(result),
            'code': code,
            'data': result
        })
    
    except Exception as e:
        logger.error(f"API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/daily-stats', methods=['GET'])
def api_daily_stats():
    """获取每日统计"""
    try:
        days = request.args.get('days', API_HISTORY_DAYS, type=int)
        
        db = Database()
        db.connect()
        data = DailyRankingModel.get_range(db, days)
        db.disconnect()
        
        result = []
        for row in data:
            result.append({
                'date': row[1],
                'avg_volume': row[2],
                'max_volume': row[3],
                'min_volume': row[4],
                'avg_price': row[5],
                'total_records': row[6]
            })
        
        return jsonify({
            'success': True,
            'count': len(result),
            'data': result
        })
    
    except Exception as e:
        logger.error(f"API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """获取全局统计"""
    try:
        db = Database()
        db.connect()
        
        latest = StockVolumeModel.get_latest(db, 1)
        dates = StockVolumeModel.get_all_dates(db)
        logs = CrawlerLogModel.get_latest(db, 1)
        
        db.disconnect()
        
        stats = {
            'total_stocks': len(latest) if latest else 0,
            'total_dates': len(dates) if dates else 0,
            'last_crawl_time': logs[0][2] if logs else 'N/A',
            'last_crawl_source': logs[0][4] if logs else 'N/A',
            'last_crawl_status': logs[0][3] if logs else 'N/A'
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
    
    except Exception as e:
        logger.error(f"API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/crawler-logs', methods=['GET'])
def api_crawler_logs():
    """获取爬虫日志"""
    try:
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 500)
        
        db = Database()
        db.connect()
        data = CrawlerLogModel.get_latest(db, limit)
        db.disconnect()
        
        result = []
        for row in data:
            result.append({
                'date': row[1],
                'time': row[2],
                'status': row[3],
                'source': row[4],
                'count': row[5],
                'message': row[6],
                'duration': row[7]
            })
        
        return jsonify({
            'success': True,
            'count': len(result),
            'data': result
        })
    
    except Exception as e:
        logger.error(f"API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dates', methods=['GET'])
def api_dates():
    """获取所有日期"""
    try:
        db = Database()
        db.connect()
        dates = StockVolumeModel.get_all_dates(db)
        db.disconnect()
        
        result = [str(d[0]) for d in dates] if dates else []
        
        return jsonify({
            'success': True,
            'count': len(result),
            'data': result
        })
    
    except Exception as e:
        logger.error(f"API错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/crawl-now', methods=['POST'])
def api_crawl_now():
    """立即执行爬虫"""
    try:
        logger.info("收到立即爬虫请求")
        crawler = StockCrawler()
        result = crawler.crawl()
        
        if result:
            return jsonify({'success': True, 'message': '爬虫执行成功'})
        else:
            return jsonify({'success': False, 'error': '爬虫执行失败'}), 500
    
    except Exception as e:
        logger.error(f"爬虫执行异常: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ Error Handlers ============

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error='页面不存在'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('error.html', error='服务器错误'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=FLASK_DEBUG)
