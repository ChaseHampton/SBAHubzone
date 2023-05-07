create or replace procedure update_search_is_searched(sid integer)
language sql
as $$
update searches set is_searched = true where search_id = sid;
$$;