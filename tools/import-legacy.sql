INSERT INTO locations
SELECT _id,name,name,name,name,name,name,replace(map,'.png','') FROM legacy.locations;

INSERT INTO items
SELECT i._id, i.name,i.name,i.name,i.name,i.name,i.jpn_name,
       CASE WHEN i.type IN ('Armor','Weapon','Decoration') THEN i.type ELSE '' END,
       COALESCE(a.slot,w.wtype,''), i.rarity,i.carry_capacity,i.buy,i.sell,
       COALESCE(i.description,''), '', '', '', '', '',
       icon(i.type,i.icon_name,COALESCE(a.slot,w.wtype,'')), icon_color(i.icon_name), i.type='Account'
FROM legacy.items i
LEFT JOIN legacy.armor a USING (_id)
LEFT JOIN legacy.weapons w USING (_id);

INSERT INTO armor (_id,slot,defense,max_defense,fire_res,thunder_res,dragon_res,water_res,ice_res,gender,hunter_type,num_slots)
SELECT _id,slot,defense,max_defense,fire_res,thunder_res,dragon_res,water_res,ice_res,
       CASE gender WHEN 'Male' THEN 0 WHEN 'Female' THEN 1 ELSE 2 END,
       CASE hunter_type WHEN 'Blade' THEN 0 WHEN 'Gunner' THEN 1 ELSE 2 END,num_slots
FROM legacy.armor;

INSERT INTO decorations SELECT * FROM legacy.decorations;
INSERT INTO combining SELECT * FROM legacy.combining;
INSERT INTO item_to_skill_tree SELECT * FROM legacy.item_to_skill_tree;
INSERT INTO components
SELECT _id,created_item_id,component_item_id,quantity,
       CASE type WHEN 'Create A' THEN 'Create' ELSE type END,0
FROM legacy.components;

INSERT INTO skill_trees
SELECT _id,name,name,name,name,name,COALESCE(jpn_name,'') FROM legacy.skill_trees;
INSERT INTO skills
SELECT _id,skill_tree_id,required_skill_tree_points,name,name,name,name,name,jpn_name,description,'','','','',''
FROM legacy.skills;

INSERT INTO monsters
SELECT _id,CASE class WHEN 'Boss' THEN '0' ELSE '1' END,
       name,name,name,name,name,'',0,icon('Monster',icon_name,name),sort_name,0
FROM legacy.monsters;
INSERT INTO monster_damage SELECT * FROM legacy.monster_damage;

CREATE TABLE mh3u_arena_times (
    quest_id INTEGER PRIMARY KEY REFERENCES quests(_id),
    participants INTEGER NOT NULL,
    time_s TEXT NOT NULL,
    time_a TEXT NOT NULL,
    time_b TEXT NOT NULL
);
CREATE TABLE mh3u_quest_reward_regions (
    reward_id INTEGER PRIMARY KEY REFERENCES quest_rewards(_id),
    region TEXT NOT NULL
);
