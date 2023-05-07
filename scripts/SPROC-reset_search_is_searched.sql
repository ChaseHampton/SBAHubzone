create or replace procedure reset_search_is_searched()
language sql 
as $$
update searches set is_searched = true;
$$;