set @startDate = date('2010-2-13');
set @startDate = (select timestamp(@startDate, curtime()));
set @time = concat(2000, ':', 4000);
set @endDate = (select date_add(@startDate, interval @time hour_minute));
set @timeStampDiff = timestampdiff(hour, @startDate, @endDate);
select @startDate as startDate, @timeStampDiff as timeStampDiff;