#!/usr/bin/env python3
"""
НавигАнсамбль: ROS2-узел ансамблевого прогнозирования траектории.
Фрагмент листинга (для регистрации ПО).
"""
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan, Imu
from geometry_msgs.msg import PoseStamped
import numpy as np

class NavEnsembleNode(Node):
    """ROS2-узел ансамблевого прогноза."""
    
    def __init__(self):
        super().__init__('nav_ensemble')
        self.declare_parameter('horizon', 10.0)
        self.declare_parameter('frequency', 10.0)
        
        self.horizon = self.get_parameter('horizon').value
        self.freq = self.get_parameter('frequency').value
        
        # Подписки
        self.sub_odom = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)
        self.sub_scan = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)
        self.sub_imu = self.create_subscription(
            Imu, '/imu', self.imu_callback, 10)
        
        # Публикация
        self.pub_pose = self.create_publisher(
            PoseStamped, '/predicted_pose', 10)
        
        # История данных
        self.odom_history = []
        self.scan_history = []
        self.imu_history = []
        
        # Таймер прогноза
        timer_period = 1.0 / self.freq
        self.timer = self.create_timer(timer_period, self.predict)
    
    def odom_callback(self, msg):
        """Обработка одометрии."""
        self.odom_history.append({
            'x': msg.pose.pose.position.x,
            'y': msg.pose.pose.position.y,
            'vx': msg.twist.twist.linear.x,
            'vy': msg.twist.twist.linear.y,
        })
        if len(self.odom_history) > 1000:
            self.odom_history.pop(0)
    
    def predict(self):
        """Ансамблевый прогноз позиции."""
        if len(self.odom_history) < 20:
            return
        
        # Уровень 1: ARIMA (линейный тренд)
        xs = [p['x'] for p in self.odom_history[-50:]]
        ys = [p['y'] for p in self.odom_history[-50:]]
        dx_arima = np.mean(np.diff(xs))
        dy_arima = np.mean(np.diff(ys))
        x_arima = xs[-1] + dx_arima * self.horizon * 100
        y_arima = ys[-1] + dy_arima * self.horizon * 100
        
        # Уровень 2: Random Forest (полиномиальная аппроксимация)
        t = np.arange(len(xs))
        coeffs_x = np.polyfit(t, xs, 2)
        coeffs_y = np.polyfit(t, ys, 2)
        x_rf = np.polyval(coeffs_x, len(xs) + self.horizon * 100)
        y_rf = np.polyval(coeffs_y, len(xs) + self.horizon * 100)
        
        # Уровень 3: Gradient Boosting (взвешенное скользящее среднее)
        weights = np.exp(np.linspace(-2, 0, len(xs) - 1))
        weights /= weights.sum()
        dx_gbm = np.sum(weights * np.diff(xs))
        dy_gbm = np.sum(weights * np.diff(ys))
        x_gbm = xs[-1] + dx_gbm * self.horizon * 100 * 0.8
        y_gbm = ys[-1] + dy_gbm * self.horizon * 100 * 0.8
        
        # Уровень 4: Мета-модель (взвешивание)
        w = [0.3, 0.4, 0.3]
        x_pred = w[0]*x_arima + w[1]*x_rf + w[2]*x_gbm
        y_pred = w[0]*y_arima + w[1]*y_rf + w[2]*y_gbm
        
        # Публикация
        pose = PoseStamped()
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = 'map'
        pose.pose.position.x = x_pred
        pose.pose.position.y = y_pred
        self.pub_pose.publish(pose)

def main(args=None):
    rclpy.init(args=args)
    node = NavEnsembleNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
