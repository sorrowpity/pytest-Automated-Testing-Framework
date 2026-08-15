-- =============================================
-- 自动化测试框架 - MySQL 初始化脚本
-- 用法: mysql -u root -p < init_mysql.sql
-- =============================================

-- 1. 创建数据库
CREATE DATABASE IF NOT EXISTS mydb
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_general_ci;

USE mydb;

-- 2. 管理员表
CREATE TABLE IF NOT EXISTS sp_manager (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    mg_name     VARCHAR(100) NOT NULL,
    mg_pwd      VARCHAR(100) NOT NULL,
    mg_state    TINYINT DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 用户表
CREATE TABLE IF NOT EXISTS sp_user (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    username    VARCHAR(100) NOT NULL,
    password    VARCHAR(100) NOT NULL,
    state       TINYINT DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. 商品分类表
CREATE TABLE IF NOT EXISTS sp_category (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    cat_name    VARCHAR(100) NOT NULL,
    cat_pid     INT DEFAULT 0,
    cat_level   INT DEFAULT 0,
    cat_deleted TINYINT DEFAULT 0,
    cat_icon    VARCHAR(500) DEFAULT '',
    cat_src     VARCHAR(500) DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. 商品属性表
CREATE TABLE IF NOT EXISTS sp_attribute (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    attr_name   VARCHAR(100) NOT NULL,
    cat_id      INT DEFAULT 0,
    attr_sel    VARCHAR(50) DEFAULT '',
    attr_write  VARCHAR(50) DEFAULT '',
    attr_vals   VARCHAR(1000) DEFAULT '',
    delete_time BIGINT DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. 商品表
CREATE TABLE IF NOT EXISTS sp_goods (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    goods_name      VARCHAR(200) NOT NULL,
    goods_price     DECIMAL(10,2) DEFAULT 0.00,
    goods_number    INT DEFAULT 0,
    goods_weight    INT DEFAULT 0,
    cat_id          INT DEFAULT 0,
    goods_introduce TEXT,
    goods_big_logo  VARCHAR(500) DEFAULT '',
    goods_small_logo VARCHAR(500) DEFAULT '',
    goods_state     INT DEFAULT 0,
    add_time        BIGINT DEFAULT 0,
    is_del          TINYINT DEFAULT 0,
    hot_mumber      INT DEFAULT 0,
    is_promote      TINYINT DEFAULT 0,
    upd_time        BIGINT DEFAULT NULL,
    delete_time     BIGINT DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. 购物车表
CREATE TABLE IF NOT EXISTS sp_cart (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    user_id     INT NOT NULL,
    goods_id    INT NOT NULL,
    goods_num   INT DEFAULT 1,
    add_time    BIGINT DEFAULT 0,
    KEY idx_cart_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. 订单表
CREATE TABLE IF NOT EXISTS sp_order (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    order_number VARCHAR(100) NOT NULL,
    user_id     INT NOT NULL,
    total_price DECIMAL(10,2) DEFAULT 0.00,
    pay_status  TINYINT DEFAULT 0,
    order_status TINYINT DEFAULT 0,
    create_time BIGINT DEFAULT 0,
    pay_time    BIGINT DEFAULT NULL,
    KEY idx_order_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. 订单明细表
CREATE TABLE IF NOT EXISTS sp_order_item (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    order_id    INT NOT NULL,
    goods_id    INT NOT NULL,
    goods_num   INT NOT NULL,
    goods_price DECIMAL(10,2) DEFAULT 0.00,
    KEY idx_item_order (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. 初始数据（幂等：先去重，再确保存在一条 admin）

-- 10.1 去重：sp_manager 每个 mg_name 只保留 id 最小的一条
DELETE t1 FROM sp_manager t1
JOIN sp_manager t2 ON t1.mg_name = t2.mg_name AND t1.id > t2.id;

-- 10.2 去重：sp_user 每个 username 只保留 id 最小的一条
DELETE t1 FROM sp_user t1
JOIN sp_user t2 ON t1.username = t2.username AND t1.id > t2.id;

-- 10.3 确保存在 admin（不存在才插入，可反复执行）
INSERT INTO sp_manager (mg_name, mg_pwd, mg_state)
SELECT 'admin', '123456', 1 FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM sp_manager WHERE mg_name = 'admin');

INSERT INTO sp_user (username, password, state)
SELECT 'admin', '123456', 1 FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM sp_user WHERE username = 'admin');
