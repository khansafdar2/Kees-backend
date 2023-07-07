use ecomm_db;

select * from cms_page;
select * from cms_seo;
select * from cms_template;
select * from cms_preferences;
select * from cms_menuitem;

SELECT * FROM authentication_user;
SELECT * FROM authentication_userinvitation;
SELECT * FROM authentication_userlastlogin;
SELECT * FROM authentication_rolepermission;
SELECT * FROM authentication_activitystream;
SELECT * FROM products_product where id=103;
SELECT * FROM products_product_collection;
SELECT * FROM products_variant;
SELECT * FROM products_inventoryhistory;
SELECT * FROM products_option where product_id=1;
SELECT * FROM products_productgroup;
SELECT * FROM products_media;
SELECT * FROM products_producttype;
SELECT * FROM products_brand;
SELECT * FROM products_collection;
SELECT * FROM products_collection_main_category;
SELECT * FROM products_collection_sub_category;
SELECT * FROM products_collection_super_sub_category;
SELECT * FROM products_collectionhandle;
SELECT * FROM products_collectionmetadata;
SELECT * FROM products_maincategory;
SELECT * FROM products_maincategorymetadata;
SELECT * FROM products_subcategory;
SELECT * FROM products_subcategorymetadata;
SELECT * FROM products_subcategorycondition;
SELECT * FROM products_supersubcategory;
SELECT * FROM products_supersubcategorymetadata;
SELECT * FROM vendor_vendor; 
SELECT * FROM setting_storeinformation; 
SELECT * FROM setting_tax;

select * from products_collection_sub_category where subcategory_id=24;
select * from products_product_collection where collection_id=9;

SELECT * FROM crm_customer;
SELECT * FROM crm_address;
SELECT * FROM crm_notes;
SELECT * FROM crm_tags;

set foreign_key_checks=0;
set foreign_key_checks=1;

truncate cms_page;
truncate cms_preferences;
truncate cms_homepage;
truncate crm_customer;
truncate crm_address;
truncate products_maincategory;
truncate products_subcategory;
truncate products_supersubcategory;
truncate products_maincategorymetadata;
truncate products_subcategorymetadata;
truncate products_supersubcategorymetadata;
truncate products_collection;
truncate products_collectionhandle;
truncate products_collectionmetadata;
truncate products_product_collection;
truncate products_product;
truncate products_media;
truncate products_variant;
truncate products_option;
truncate products_inventoryhistory;
truncate products_productgroup;