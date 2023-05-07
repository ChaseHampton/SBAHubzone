create or replace procedure update_business_is_searched(bid integer)
language sql
as $$
update businesses set is_searched = true where businesses_id = bid;
$$;