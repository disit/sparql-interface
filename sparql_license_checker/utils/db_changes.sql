alter table licenses add link varchar(1000);

alter table lic_perm_cond add duty tinyint;
update lic_perm_cond set duty = 0;
update lic_perm_cond set duty = 1 where description in ('Sharealike','attribution');

commit;
