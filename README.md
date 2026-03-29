## beat
你目前单实例 --concurrency=1 的场景，--beat 内嵌是最简洁的做法，没有任何问题。
唯一要注意的就是 Claude 已经提到的：将来如果你扩容成多个 worker 容器，必须把 beat 拆出来单独跑，否则每个 worker 都会触发定时任务，重复执行。到那时候的配置是：
yaml# worker（多实例，不带 beat）
celery -A ... worker -Q celery,email,default --concurrency=4

beat（单独一个容器，只负责调度）
*celery -A ... b*eat -l info
但现在博客项目单机部署，现在的方案就是最优解，不用过度设计。

## celery 

1. 启动 Celery Worker：`celery -A src.core.celery_app.celery_app worker -P eventlet -l info`
   * **`-A celery_task.celery`**：指向你的 Celery 实例所在的文件。`celery_task` 是目录，`celery` 是文件名（不需要加 `.py` 扩展名）。
2. 启动 Celery Beat：`celery -A src.core.celery_app.celery_app beat -l info`