SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ; START TRANSACTION WITH CONSISTENT SNAPSHOT;
SELECT JSON_OBJECT('table','m1','id',id,'agent_id',agent_id,'data',data,'path',path,'asl_file_path',asl_file_path,'processed',processed,'created_at',created_at,'updated_at',updated_at) FROM m1 ORDER BY id;
SELECT JSON_OBJECT('table','m2','id',id,'agent_id',agent_id,'data',data,'path',path,'asl_file_path',asl_file_path,'processed',processed,'created_at',created_at,'updated_at',updated_at) FROM m2 ORDER BY id;
SELECT JSON_OBJECT('table','m3','id',id,'agent_id',agent_id,'data',data,'path',path,'asl_file_path',asl_file_path,'processed',processed,'created_at',created_at,'updated_at',updated_at) FROM m3 ORDER BY id;
SELECT JSON_OBJECT('table','router','id',id,'agent_id',agent_id,'data',data,'path',path,'asl_file_path',asl_file_path,'processed',processed,'created_at',created_at,'updated_at',updated_at) FROM router ORDER BY id;
COMMIT;