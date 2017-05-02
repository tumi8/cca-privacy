pragma temp_store = 2;
CREATE VIEW IF NOT EXISTS connections_apple_days AS select *,strftime('%d-%m-%Y',timestamp,'unixepoch','localtime') AS day from connections_apple;
CREATE VIEW IF NOT EXISTS relations_apple_wo_bruegge AS select * from relations_apple WHERE conKey != '77A0286C7B3407F4C03356F1782CBF1E';
SELECT COUNT(DISTINCT(ca.day)), ra.conKey FROM connections_apple_days ca, relations_apple_wo_bruegge ra WHERE ca.conKey=ra.certKey GROUP BY ra.conKey ORDER BY COUNT(DISTINCT(ca.day)) DESC;
