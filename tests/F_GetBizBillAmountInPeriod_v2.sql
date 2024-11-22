set table.exec.source.idle-timeout=5s;
set table.exec.state.ttl=10min;
set table.local-time-zone=${local_time_zone};
set table.exec.emit.early-fire.enabled=true;
set table.exec.emit.early-fire.delay=3s;
set table.exec.sink.not-null-enforcer=DROP;


-- 金额表关联计划表
-- dimension table
create table hbase_dimension_table (
     plan_no STRING,
     cf Row<user_id STRING, biz_type STRING, clear_status STRING, overdue_status STRING,
        month_due_timestamp STRING,bill_date_timestamp STRING, clear_time STRING, term_num STRING, plan_update_time String,
        principal_repayable STRING, total_amount_repayable STRING, total_amount_repaid String, total_amount_refund STRING, total_amount_deduct String>
) with (
    'connector' = 'hbase-2.2',
    'table-name' = 'paredose_credit_live_id:id_metrics_biz_dimension_plan_tab',
    'zookeeper.quorum' = '${hbase.zookeeper.quorum}',
    'zookeeper.znode.parent' = '/hbase',
    'sink.buffer-flush.interval' = '500ms',
    'sink.buffer-flush.max-size' = '1mb',
    'sink.buffer-flush.max-rows' = '100',
    'lookup.async' = 'true',
    'lookup.max-retries' = '10'
);

create table kafka_plan_money_category_source (
    _event Row (
        database String,
        `table` String,
        type String
    ),
    plan_no String,
    biz_type Integer,
    money_category Integer,
    principal decimal(30, 10),
    interest decimal(30, 10),
    fee1 decimal(30, 10),
    fee2 decimal(30, 10),
    fee3 decimal(30, 10),
    fee4 decimal(30, 10),
    fee5 decimal(30, 10),
    fee6 decimal(30, 10),
    fee7 decimal(30, 10),
    fee8 decimal(30, 10),
    create_time String,
    update_time String,
    proc_time AS PROCTIME()
)WITH (
 	-- declare the external system to connect to
 	'connector' = 'kafka',
 	'topic' = 'di.credit_core_debt_cl_id_db__plan_money_category_tab__live;di.credit_core_debt_spl_id_db__plan_money_category_tab__live',
 	--'scan.startup.mode' = 'earliest-offset',
  'scan.startup.mode' = 'timestamp',
  'scan.startup.timestamp-millis' = '1704988800000',
 	'properties.auto.offset.reset' = 'earliest',
    ${table.config.common},
    ${di.table.config.sasl},
    'properties.bootstrap.servers' = '${di.bootstrap.servers.sasl}',
    'properties.group.id' = 'paredose_credit_live_id:id_metrics_get_biz_bill_amount',
 	-- declare a format for this system
    'scan.topic-partition-discovery.interval'= '60s',
    'properties.allow.auto.create.topics' = 'false',
    'format' = 'json'
);

-- 数据过滤
create view plan_money_category_filter_view as
select
    plan_no,
    biz_type,
    money_category,
    principal,
    principal + interest + fee1 + fee2 + fee3 + fee4 + fee5 + fee6 + fee7 + fee8 as total_amount,
    substring(update_time, 0, 19) as update_time,
    cast(UNIX_TIMESTAMP(CONVERT_TZ(SUBSTRING(update_time, 0, 19),'UTC','${local_time_zone}')) as string)  AS money_update_time,
    proc_time
from kafka_plan_money_category_source
where ((_event.database like 'credit_core_debt_spl_id_db%' and _event.`table` like 'plan_money_category_tab%' and (biz_type = 3 or biz_type = 7))
    or (_event.database like 'credit_core_debt_cl_id_db%' and _event.`table` like 'plan_money_category_tab%' and biz_type = 1))
    and plan_no is not null
    and char_length(plan_no) > 0
    and money_category in (1, 3, 4)
;

-- dimension join
create view plan_money_category_dimension_view as
select
    t1.plan_no,
    t1.money_category,
    t1.total_amount,
    t1.money_update_time,
    t1.proc_time,
    --hbase_dimension_table.cf.biz_type as biz_type,
    cast(t1.biz_type as string) as biz_type,
    hbase_dimension_table.cf.user_id as user_id,
    hbase_dimension_table.cf.bill_date_timestamp as bill_date_timestamp,
    hbase_dimension_table.cf.clear_time as clear_time,
    hbase_dimension_table.cf.plan_update_time as plan_update_time,
    hbase_dimension_table.cf.total_amount_repayable as total_amount_repayable,
    hbase_dimension_table.cf.total_amount_refund as total_amount_refund,
    hbase_dimension_table.cf.total_amount_deduct as total_amount_deduct
from plan_money_category_filter_view t1 inner join hbase_dimension_table FOR SYSTEM_TIME AS OF t1.proc_time
    on (t1.plan_no || '_' || cast(t1.biz_type as String)) = hbase_dimension_table.plan_no
;

-- plan_money_category 聚合
create view plan_money_category_compare_view as
select
    user_id, plan_no,bill_date_timestamp, clear_time, biz_type, cast(plan_update_time as bigint) as plan_update_time,
    case when money_category = 1 then total_amount
        when money_category <> 1 and total_amount_repayable is null then 0
        else cast(split_index(total_amount_repayable, '_', 1) as decimal(30, 10)) end as total_amount_repayable,

    case when money_category = 1 and total_amount_repayable is null then cast(money_update_time as bigint)
         when money_category = 1 and total_amount_repayable is not null then cast(greatest(money_update_time, split_index(total_amount_repayable, '_', 0)) as bigint)
         when money_category <> 1 and total_amount_repayable is null then 0
         when money_category <> 1 and total_amount_repayable is not null then cast(split_index(total_amount_repayable, '_', 0) as bigint) end as total_amount_repayable_time,

    case when money_category = 3 then total_amount
        when money_category <> 3 and total_amount_refund is null then 0
        else cast(split_index(total_amount_refund, '_', 1) as decimal(30, 10)) end as total_amount_refund,

    case when money_category = 3 and total_amount_refund is null then cast(money_update_time as bigint)
             when money_category = 3 and total_amount_refund is not null then cast(greatest(money_update_time, split_index(total_amount_refund, '_', 0)) as bigint)
             when money_category <> 3 and total_amount_refund is null then 0
             when money_category <> 3 and total_amount_refund is not null then cast(split_index(total_amount_refund, '_', 0) as bigint) end as total_amount_refund_time,

    case when money_category = 4 then total_amount
        when money_category <> 4 and total_amount_deduct is null then 0
        else cast(split_index(total_amount_deduct, '_', 1) as decimal(30, 10)) end as total_amount_deduct,

    case when money_category = 4 and total_amount_deduct is null then cast(money_update_time as bigint)
             when money_category = 4 and total_amount_deduct is not null then cast(greatest(money_update_time, split_index(total_amount_deduct, '_', 0)) as bigint)
             when money_category <> 4 and total_amount_deduct is null then 0
             when money_category <> 4 and total_amount_deduct is not null then cast(split_index(total_amount_deduct, '_', 0) as bigint) end as total_amount_deduct_time,

    proc_time
from plan_money_category_dimension_view
where plan_update_time is not null
    and (
        (money_category = 1 and (total_amount_repayable is null or split_index(total_amount_repayable, '_', 0) <= money_update_time))
        or (money_category = 3 and (total_amount_refund is null or split_index(total_amount_refund, '_', 0) <= money_update_time))
        or (money_category = 4 and (total_amount_deduct is null or split_index(total_amount_deduct, '_', 0) <= money_update_time))
    )
;

-- 分组聚合
create view plan_money_category_group_view as
select
    user_id, plan_no, bill_date_timestamp, clear_time, plan_update_time, biz_type,
    max(total_amount_repayable) as total_amount_repayable,
    max(total_amount_repayable_time) as total_amount_repayable_time,
    max(total_amount_refund) as total_amount_refund,
    max(total_amount_refund_time) as total_amount_refund_time,
    max(total_amount_deduct) as total_amount_deduct,
    max(total_amount_deduct_time) as total_amount_deduct_time
from table (hop(table plan_money_category_compare_view, descriptor(proc_time), interval '50' seconds, interval '1' minutes))
group by window_start, user_id, biz_type, plan_no, bill_date_timestamp, clear_time, plan_update_time
;

-- sink table
create table hbase_sink_table (
    rowkey STRING,
    cf     STRING,
    qf     STRING,
    val    STRING,
    ts     BIGINT,
    PRIMARY KEY (rowkey) NOT ENFORCED
) with (
    'connector' = 'hbase-dynamic-2.2-nodel',
    'table-name' = 'paredose_credit_live_id:id_metrics_get_biz_bill_amount_v2',
    'zookeeper.quorum' = '${hbase.zookeeper.quorum}',
    'sink.buffer-flush.interval' = '500ms',
    'sink.buffer-flush.max-size' = '1mb',
    'sink.buffer-flush.max-rows' = '100'
);

-- sink
INSERT INTO hbase_sink_table
SELECT
  SUBSTRING(MD5(user_id), 0, 2) || '_' || user_id || '_' || biz_type || '_' || bill_date_timestamp as rowkey,
  'cf' as cf,
  plan_no as qf,
  cast(amount as string) as val,
  ts
FROM
(
  SELECT
    user_id,
    plan_no,
    bill_date_timestamp,
    biz_type,
    (
      CASE
           WHEN SUBSTRING(clear_time, 0, 19) <= '1970-01-01 00:00:00' AND total_amount_repayable - total_amount_refund - total_amount_deduct > 0
                THEN total_amount_repayable - total_amount_refund - total_amount_deduct
           ELSE 0
      END
    ) AS amount,
    (plan_update_time + total_amount_repayable_time + total_amount_refund_time + total_amount_deduct_time) * 1000 as ts
    FROM plan_money_category_group_view
) where amount is not null
  and bill_date_timestamp is not null and bill_date_timestamp <> ''
;

--插入统计账单月
INSERT INTO hbase_sink_table
select 
  SUBSTRING(MD5(user_id), 0, 2) || '_' || user_id || '_' || bill_month_timestamp as rowkey,
  'cf' as cf,
  'bill_month' as qf,
  cast(bill_month as string) as val,
  ts
FROM
(
  SELECT
    user_id,
    cast(UNIX_TIMESTAMP(FROM_UNIXTIME(cast(bill_date_timestamp as bigint), 'yyyy-MM-01 00:00:00')) as string) as bill_month_timestamp,
    (
      CASE
           WHEN SUBSTRING(clear_time, 0, 19) <= '1970-01-01 00:00:00' AND total_amount_repayable - total_amount_refund - total_amount_deduct > 0
                THEN total_amount_repayable - total_amount_refund - total_amount_deduct
           ELSE 0
      END
    ) AS amount,
    FROM_UNIXTIME(cast(bill_date_timestamp as bigint), 'yyyy-MM-01') as bill_month,
    (plan_update_time + total_amount_repayable_time + total_amount_refund_time + total_amount_deduct_time) * 1000 as ts
    FROM plan_money_category_group_view where bill_date_timestamp <> ''
) where amount is not null 
  and bill_month_timestamp is not null
;

-- 计划表关联金额维表
create table kafka_plan_source (
    _event Row (
        database String,
        `table` String,
        type String
    ),
    user_id String,
    biz_type Integer,
    plan_no String,
    clear_status Integer,
    overdue_status Integer,
    due_date String,
    clear_time String,
    term_num Integer,
    create_time String,
    update_time String,
    proc_time AS PROCTIME()
)WITH (
 	'connector' = 'kafka',
 	'topic' = 'di.credit_core_debt_cl_id_db__plan_tab__live;di.credit_core_debt_spl_id_db__plan_tab__live',
 	--'scan.startup.mode' = 'earliest-offset',
  'scan.startup.mode' = 'timestamp',
  'scan.startup.timestamp-millis' = '1704988800000',
 	'properties.auto.offset.reset' = 'earliest',
    ${table.config.common},
    ${di.table.config.sasl},
    'properties.bootstrap.servers' = '${di.bootstrap.servers.sasl}',
    'properties.group.id' = 'paredose_credit_live_id:id_metrics_get_biz_bill_amount',
 	-- declare a format for this system
    'scan.topic-partition-discovery.interval'= '60s',
    'properties.allow.auto.create.topics' = 'false',
    'format' = 'json'
);

-- 数据过滤
create view plan_filter_view as
select
    plan_no,
    user_id,
    biz_type,
    CASE 
        WHEN DATE_FORMAT(CONVERT_TZ(SUBSTRING(due_date, 0, 19), 'UTC','${local_time_zone}'), 'dd') = '01' THEN cast(UNIX_TIMESTAMP(DATE_FORMAT(TO_TIMESTAMP(cast(TO_DATE(CONVERT_TZ(SUBSTRING(due_date, 0, 19), 'UTC','${local_time_zone}')) - INTERVAL '7' day as string) || ' 00:00:00', 'yyyy-MM-21 00:00:00'), 'yyyy-MM-21 00:00:00')) as string)
        WHEN DATE_FORMAT(CONVERT_TZ(SUBSTRING(due_date, 0, 19), 'UTC','${local_time_zone}'), 'dd') = '05' THEN cast(UNIX_TIMESTAMP(DATE_FORMAT(TO_TIMESTAMP(cast(TO_DATE(CONVERT_TZ(SUBSTRING(due_date, 0, 19), 'UTC','${local_time_zone}')) - INTERVAL '7' day as string) || ' 00:00:00', 'yyyy-MM-25 00:00:00'), 'yyyy-MM-25 00:00:00')) as string)
        WHEN DATE_FORMAT(CONVERT_TZ(SUBSTRING(due_date, 0, 19), 'UTC','${local_time_zone}'), 'dd') = '11' THEN cast(UNIX_TIMESTAMP(cast(TO_DATE(CONVERT_TZ(SUBSTRING(due_date, 0, 19), 'UTC','${local_time_zone}')) - INTERVAL '10' day as string) || ' 00:00:00') as string)
        WHEN DATE_FORMAT(CONVERT_TZ(SUBSTRING(due_date, 0, 19), 'UTC','${local_time_zone}'), 'dd') = '25' THEN cast(UNIX_TIMESTAMP(cast(TO_DATE(CONVERT_TZ(SUBSTRING(due_date, 0, 19), 'UTC','${local_time_zone}')) - INTERVAL '10' day as string) || ' 00:00:00') as string)
        ELSE ''
    END AS bill_date_timestamp,
    substring(clear_time, 0, 19) as clear_time,
    cast(UNIX_TIMESTAMP(CONVERT_TZ(SUBSTRING(update_time, 0, 19),'UTC','${local_time_zone}')) as bigint)  AS plan_update_time,
    proc_time
from kafka_plan_source
where _event.database like 'credit_core_debt_spl_id_db%'
    and _event.`table` like 'plan_tab%'
    and plan_no is not null
    and char_length(plan_no) > 0
    and (biz_type = 3 or biz_type = 7)
UNION ALL
select
    plan_no,
    user_id,
    biz_type,
    cast(UNIX_TIMESTAMP(DATE_FORMAT(TO_TIMESTAMP(cast(TO_DATE(CONVERT_TZ(SUBSTRING(due_date, 0, 19), 'UTC','${local_time_zone}')) - INTERVAL '9' day as string) || ' 00:00:00', 'yyyy-MM-dd 00:00:00'), 'yyyy-MM-dd 00:00:00')) as string)  AS bill_date_timestamp,
    substring(clear_time, 0, 19) as clear_time,
    cast(UNIX_TIMESTAMP(CONVERT_TZ(SUBSTRING(update_time, 0, 19),'UTC','${local_time_zone}')) as bigint)  AS plan_update_time,
    proc_time
from kafka_plan_source
where _event.database like 'credit_core_debt_cl_id_db%'
    and _event.`table` like 'plan_tab%'
    and plan_no is not null
    and char_length(plan_no) > 0
    and biz_type = 1
;

-- category dimension join
create view plan_dimension_view as
select
    t1.plan_no,
    t1.user_id,
    t1.bill_date_timestamp,
    t1.clear_time,
    t1.plan_update_time,
    --hbase_dimension_table.cf.biz_type as biz_type,
    cast(t1.biz_type as string) as biz_type,
    cast((case when hbase_dimension_table.cf.total_amount_repayable is not null then split_index(hbase_dimension_table.cf.total_amount_repayable, '_', 1) else '0' end) as decimal(30, 10)) as total_amount_repayable,
    cast((case when hbase_dimension_table.cf.total_amount_refund is not null then split_index(hbase_dimension_table.cf.total_amount_refund, '_', 1) else '0' end) as decimal(30, 10)) as total_amount_refund,
    cast((case when hbase_dimension_table.cf.total_amount_deduct is not null then split_index(hbase_dimension_table.cf.total_amount_deduct, '_', 1) else '0' end) as decimal(30, 10)) as total_amount_deduct,

    cast((case when hbase_dimension_table.cf.total_amount_repayable is not null then split_index(hbase_dimension_table.cf.total_amount_repayable, '_', 0) else '0' end) as bigint) as total_amount_repayable_time,
    cast((case when hbase_dimension_table.cf.total_amount_refund is not null then split_index(hbase_dimension_table.cf.total_amount_refund, '_', 0) else '0' end) as bigint) as total_amount_refund_time,
    cast((case when hbase_dimension_table.cf.total_amount_deduct is not null then split_index(hbase_dimension_table.cf.total_amount_deduct, '_', 0) else '0' end) as bigint) as total_amount_deduct_time,
    t1.proc_time
from plan_filter_view t1 left join hbase_dimension_table FOR SYSTEM_TIME AS OF t1.proc_time
on (t1.plan_no || '_' || cast(t1.biz_type as String)) = hbase_dimension_table.plan_no
where hbase_dimension_table.cf.plan_update_time is null
    or cast(t1.plan_update_time as string) >= hbase_dimension_table.cf.plan_update_time
;

-- sink
INSERT INTO hbase_sink_table
SELECT
  SUBSTRING(MD5(user_id), 0, 2) || '_' || user_id || '_' || biz_type || '_' || bill_date_timestamp as rowkey,
  'cf' as cf,
  plan_no as qf,
  cast(amount as string) as val,
  ts
FROM
(
  SELECT
    user_id,
    plan_no,
    bill_date_timestamp,
    biz_type,
    (
      CASE
           WHEN SUBSTRING(clear_time, 0, 19) <= '1970-01-01 00:00:00' AND total_amount_repayable - total_amount_refund - total_amount_deduct > 0
                THEN total_amount_repayable - total_amount_refund - total_amount_deduct
           ELSE 0
      END
    ) AS amount,
    (plan_update_time + total_amount_repayable_time + total_amount_refund_time + total_amount_deduct_time) * 1000 as ts
    FROM plan_dimension_view
) where amount is not null and ts is not null
  and bill_date_timestamp is not null and bill_date_timestamp <> ''
;

INSERT INTO hbase_sink_table
SELECT
  SUBSTRING(MD5(user_id), 0, 2) || '_' || user_id || '_' || bill_month_timestamp as rowkey,
  'cf' as cf,
  'bill_month' as qf,
  cast(bill_month as string) as val,
  ts
FROM
(
  SELECT
    user_id,
    cast(UNIX_TIMESTAMP(FROM_UNIXTIME(cast(bill_date_timestamp as bigint), 'yyyy-MM-01 00:00:00')) as string) as bill_month_timestamp,
    (
      CASE
           WHEN SUBSTRING(clear_time, 0, 19) <= '1970-01-01 00:00:00' AND total_amount_repayable - total_amount_refund - total_amount_deduct > 0
                THEN total_amount_repayable - total_amount_refund - total_amount_deduct
           ELSE 0
      END
    ) AS amount,
    FROM_UNIXTIME(cast(bill_date_timestamp as bigint), 'yyyy-MM-01') as bill_month,
    (plan_update_time + total_amount_repayable_time + total_amount_refund_time + total_amount_deduct_time) * 1000 as ts
    FROM plan_dimension_view where bill_date_timestamp <> ''
) where amount is not null and ts is not null
  and bill_month_timestamp is not null
;

-- 双流关联
-- join
create view plan_join_view as
select
    p1.user_id,
    p1.plan_no,
    p1.biz_type,
    p1.bill_date_timestamp,
    p1.clear_time,
    p1.plan_update_time,
    p1.total_amount_repayable,
    p1.total_amount_refund,
    p1.total_amount_deduct,
    p1.total_amount_repayable_time,
    p1.total_amount_refund_time,
    p1.total_amount_deduct_time,
    p2.money_category,
    p2.total_amount,
    p2.money_update_time
from plan_dimension_view p1 inner join plan_money_category_filter_view p2
on (p1.plan_no || '_' || p1.biz_type) = (p2.plan_no || '_' || cast(p2.biz_type as string))
where p1.proc_time BETWEEN p2.proc_time - INTERVAL '1' MINUTE
    and p2.proc_time + INTERVAL '1' MINUTE;

-- 取最新的关联数据
create view plan_join_latest_view as
select
    *
from (
    select
        *, ROW_NUMBER() OVER (
                       PARTITION BY plan_no, money_category
                       ORDER BY plan_update_time desc, money_update_time desc
                     ) AS rownum
    from plan_join_view
) where rownum <= 1;

-- money表聚合
create view plan_join_group_view as
select
    user_id, plan_no, bill_date_timestamp, clear_time, plan_update_time,biz_type,

    max(case when money_category = 1 and total_amount_repayable_time <= money_update_time then total_amount
             else total_amount_repayable end) as total_amount_repayable,
    max(case when money_category = 1 then cast(greatest(cast(total_amount_repayable_time as string), money_update_time) as bigint)
             else total_amount_repayable_time end) as total_amount_repayable_time,

    max(case when money_category = 3 and total_amount_refund_time <= money_update_time then total_amount
             else total_amount_refund end) as total_amount_refund,
    max(case when money_category = 3 then cast(greatest(cast(total_amount_refund_time as string), money_update_time) as bigint)
                 else total_amount_refund_time end) as total_amount_refund_time,

    max(case when money_category = 4 and total_amount_deduct_time <= money_update_time then total_amount
             else total_amount_deduct end) as total_amount_deduct,
    max(case when money_category = 4 then cast(greatest(cast(total_amount_deduct_time as string), money_update_time) as bigint)
                 else total_amount_deduct_time end) as total_amount_deduct_time
from plan_join_latest_view
group by user_id, biz_type, plan_no, bill_date_timestamp, clear_time, plan_update_time;

-- 写入结果
INSERT INTO hbase_sink_table
SELECT
  SUBSTRING(MD5(user_id), 0, 2) || '_' || user_id || '_' || biz_type || '_' || bill_date_timestamp as rowkey,
  'cf' as cf,
  plan_no as qf,
  cast(amount as string) as val,
  ts
FROM
(
  SELECT
    user_id,
    plan_no,
    bill_date_timestamp,
    biz_type,
    (
      CASE
           WHEN SUBSTRING(clear_time, 0, 19) <= '1970-01-01 00:00:00' AND total_amount_repayable - total_amount_refund - total_amount_deduct > 0
                THEN total_amount_repayable - total_amount_refund - total_amount_deduct
           ELSE 0
      END
    ) AS amount,
    (plan_update_time + total_amount_repayable_time + total_amount_refund_time + total_amount_deduct_time) * 1000 as ts
    FROM plan_join_group_view
) where amount is not null
  and bill_date_timestamp is not null and bill_date_timestamp <> ''
;

INSERT INTO hbase_sink_table
SELECT
  SUBSTRING(MD5(user_id), 0, 2) || '_' || user_id || '_' || bill_month_timestamp as rowkey,
  'cf' as cf,
  'bill_month' as qf,
  cast(bill_month as string) as val,
  ts
FROM
(
  SELECT
    user_id,
    cast(UNIX_TIMESTAMP(FROM_UNIXTIME(cast(bill_date_timestamp as bigint), 'yyyy-MM-01 00:00:00')) as string) as bill_month_timestamp,
    (
      CASE
           WHEN SUBSTRING(clear_time, 0, 19) <= '1970-01-01 00:00:00' AND total_amount_repayable - total_amount_refund - total_amount_deduct > 0
                THEN total_amount_repayable - total_amount_refund - total_amount_deduct
           ELSE 0
      END
    ) AS amount,
    FROM_UNIXTIME(cast(bill_date_timestamp as bigint), 'yyyy-MM-01') as bill_month,
    (plan_update_time + total_amount_repayable_time + total_amount_refund_time + total_amount_deduct_time) * 1000 as ts
    FROM plan_join_group_view where bill_date_timestamp <> ''
) where amount is not null
  and bill_month_timestamp is not null
;