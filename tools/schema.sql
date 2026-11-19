CREATE TABLE "android_metadata" ("locale" TEXT DEFAULT 'en_US');

CREATE TABLE `armor` (
  `_id` integer primary key autoincrement,
  `slot` text NOT NULL,
  `defense` integer NOT NULL,
  `max_defense` integer,
  `fire_res` integer NOT NULL,
  `thunder_res` integer NOT NULL,
  `dragon_res` integer NOT NULL,
  `water_res` integer NOT NULL,
  `ice_res` integer NOT NULL,
  `gender` integer NOT NULL,
  `hunter_type` integer NOT NULL,
  `num_slots` integer,
  `family` integer
);

CREATE TABLE `armor_families`(
	`_id` integer primary key,
	`name` text NOT NULL,
	`name_de` text NOT NULL,
	`name_fr` text NOT NULL,
	`name_es` text NOT NULL,
	`name_it` text NOT NULL,
	`name_ja` text DEFAULT NULL,
	`rarity` integer NOT NULL,
	`head_id` integer NOT NULL,
	`body_id` integer NOT NULL,
	`arms_id` integer NOT NULL,
	`waist_id` integer NOT NULL,
	`legs_id` integer NOT NULL,
	`hunter_type` integer NOT NULL
);

CREATE TABLE `asb_sets` (
  `_id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name`  TEXT NOT NULL,
  `rank`  INTEGER NOT NULL,
  `hunter_type` INTEGER NOT NULL,
  `head_armor`  INTEGER,
  `head_decoration_1` INTEGER,
  `head_decoration_2` INTEGER,
  `head_decoration_3` INTEGER,
  `body_armor`  INTEGER,
  `body_decoration_1` INTEGER,
  `body_decoration_2` INTEGER,
  `body_decoration_3` INTEGER,
  `arms_armor`  INTEGER,
  `arms_decoration_1` INTEGER,
  `arms_decoration_2` INTEGER,
  `arms_decoration_3` INTEGER,
  `waist_armor` INTEGER,
  `waist_decoration_1`  INTEGER,
  `waist_decoration_2`  INTEGER,
  `waist_decoration_3`  INTEGER,
  `legs_armor`  INTEGER,
  `legs_decoration_1` INTEGER,
  `legs_decoration_2` INTEGER,
  `legs_decoration_3` INTEGER,
  `talisman_exists` INTEGER NOT NULL,
  `talisman_type` INTEGER,
  `talisman_slots`  INTEGER,
  `talisman_decoration_1` INTEGER,
  `talisman_decoration_2` INTEGER,
  `talisman_decoration_3` INTEGER,
  `talisman_skill_1`  INTEGER,
  `talisman_skill_1_points` INTEGER,
  `talisman_skill_2`  INTEGER,
  `talisman_skill_2_points` INTEGER,
  `weapon_slots` INTEGER,
  `weapon_decoration_1` INTEGER,
  `weapon_decoration_2` INTEGER,
  `weapon_decoration_3` INTEGER
);

CREATE TABLE `charms` (
  `_id` integer primary key autoincrement,
  `num_slots` integer NOT NULL,
  `skill_tree_1_id` integer NOT NULL,
  `skill_tree_1_amount` integer NOT NULL,
  `skill_tree_2_id` integer DEFAULT NULL,
  `skill_tree_2_amount` integer DEFAULT NULL,
  foreign key(`skill_tree_1_id`) references skill_trees(`_id`),
  foreign key(`skill_tree_2_id`) references skill_trees(`_id`)
);

CREATE TABLE `combining` (
  `_id` integer primary key autoincrement,
  `created_item_id` integer NOT NULL,
  `item_1_id` integer NOT NULL,
  `item_2_id` integer NOT NULL,
  `amount_made_min` integer NOT NULL,
  `amount_made_max` integer NOT NULL,
  `percentage` integer NOT NULL,
  foreign key(`created_item_id`) references items(`_id`),
  foreign key(`item_1_id`) references items(`_id`),
  foreign key(`item_2_id`) references items(`_id`)
);

CREATE TABLE `components` (
  `_id` integer primary key autoincrement,
  `created_item_id` integer NOT NULL,
  `component_item_id` integer NOT NULL,
  `quantity` integer NOT NULL,
  `type` text DEFAULT NULL,
  `key` integer NOT NULL,
  foreign key(`created_item_id`) references items(`_id`),
  foreign key(`component_item_id`) references items(`_id`)
);

CREATE TABLE `decorations` (
  `_id` integer primary key autoincrement,
  `num_slots` integer NOT NULL
);

CREATE TABLE `felyne_skills` (
  `_id` integer primary key autoincrement,
  `skill_name` text NOT NULL,
  `description` text NOT NULL
);

CREATE TABLE `food_combos` (
  `_id` integer primary key autoincrement,
  `ingredient1` text NOT NULL,
  `ingredient2` text NOT NULL,
  `cooked` text NOT NULL,
  `bonus` text NOT NULL,
  `skill1_id` integer,
  `skill2_id` integer,
  `skill3_id` integer,
  foreign key(`skill1_id`) references felyne_skills(`_id`),
  foreign key(`skill2_id`) references felyne_skills(`_id`),
  foreign key(`skill3_id`) references felyne_skills(`_id`)
);

CREATE TABLE `gathering` (
  `_id` integer primary key autoincrement,
  `item_id` integer NOT NULL,
  `location_id` integer NOT NULL,
  `area` text NOT NULL,
  `site` text NOT NULL,
  `rank` text NOT NULL,
  `fixed` integer DEFAULT 0,
  `rare` integer DEFAULT 0,
  `group_num` integer DEFAULT 0,
  `quantity` integer DEFAULT NULL,
  `percentage` integer DEFAULT NULL,
  foreign key(`item_id`) references items(`_id`),
  foreign key(`location_id`) references locations(`_id`)
);

CREATE TABLE `horn_melodies` (
  `_id` integer primary key autoincrement,
  `notes` text NOT NULL,
  `song` text NOT NULL,
  `name` text NOT NULL,
  `name_de` text NOT NULL,
  `name_fr` text NOT NULL,
  `name_es` text NOT NULL,
  `name_it` text NOT NULL,
  `name_ja` text DEFAULT NULL,
  `effect1` text NOT NULL,
  `effect1_de` text NOT NULL,
  `effect1_fr` text NOT NULL,
  `effect1_es` text NOT NULL,
  `effect1_it` text NOT NULL,
  `effect1_ja` text DEFAULT NULL,
  `effect2` text NOT NULL,
  `effect2_de` text NOT NULL,
  `effect2_fr` text NOT NULL,
  `effect2_es` text NOT NULL,
  `effect2_it` text NOT NULL,
  `effect2_ja` text DEFAULT NULL,
  `duration` text NOT NULL,
  `extension` text NOT NULL
);

CREATE TABLE `hunting_rewards` (
  `_id` integer primary key autoincrement,
  `item_id` integer NOT NULL,
  `condition` text NOT NULL,
  `monster_id` integer NOT NULL,
  `rank` text NOT NULL,
  `stack_size` integer NOT NULL,
  `percentage` int(10) NOT NULL,
  foreign key(`item_id`) references items(`_id`),
  foreign key(`monster_id`) references monsters(`_id`)
);

CREATE TABLE `ingredients` (
  `_id` integer primary key autoincrement,
  `ingredient` text NOT NULL,
  `name` text NOT NULL,
  `level` integer,
  `quest_id` integer,
  foreign key(`quest_id`) references quests(`_id`)
);

CREATE TABLE `item_to_material` (
  `_id` integer primary key autoincrement,
  `item_id` integer NOT NULL,
  `material_item_id` integer NOT NULL,
  `amount` integer NOT NULL
);

CREATE TABLE `item_to_quest` (
  `_id` integer primary key autoincrement,
  `item_id` integer NOT NULL,
  `quest_id` integer NOT NULL,
  foreign key(`item_id`) references items(`_id`),
  foreign key(`quest_id`) references quests(`_id`)
);

CREATE TABLE `item_to_skill_tree` (
  `_id` integer primary key autoincrement,
  `item_id` integer NOT NULL,
  `skill_tree_id` integer NOT NULL,
  `point_value` integer NOT NULL,
  foreign key(`item_id`) references items(`_id`),
  foreign key(`skill_tree_id`) references skill_trees(`_id`)
);

CREATE TABLE `items` (
  `_id` integer primary key autoincrement,
  `name` text NOT NULL,
  `name_de` text NOT NULL,
  `name_fr` text NOT NULL,
  `name_es` text NOT NULL,
  `name_it` text NOT NULL,
  `name_ja` text DEFAULT NULL,
  `type` text NOT NULL,
  `sub_type` text NOT NULL,
  `rarity` integer NOT NULL DEFAULT 0,
  `carry_capacity` integer NOT NULL DEFAULT 0,
  `buy` mediumint(8) DEFAULT NULL,
  `sell` integer DEFAULT NULL,
  `description` text DEFAULT NULL,
  `description_de` text NOT NULL,
  `description_fr` text NOT NULL,
  `description_es` text NOT NULL,
  `description_it` text NOT NULL,
  `description_ja` text NOT NULL,
  `icon_name` text DEFAULT NULL,
  `icon_color` int NOT NULL,
  `account` int NOT NULL
);

CREATE TABLE `locations` (
  `_id` integer primary key autoincrement,
  `name` text UNIQUE NOT NULL,
  `name_de` text NOT NULL,
  `name_fr` text NOT NULL,
  `name_es` text NOT NULL,
  `name_it` text NOT NULL,
  `name_ja` text NOT NULL,
  `map` text NOT NULL
);

CREATE TABLE `meow_locations` (
  `_id` integer primary key,
  `name` text NOT NULL,
  `name_de` text NOT NULL,
  `name_fr` text NOT NULL,
  `name_es` text NOT NULL,
  `name_it` text NOT NULL,
  `name_ja` text DEFAULT NULL
);

CREATE TABLE `meow_rewards` (
  `_id` integer primary key autoincrement,
  `meow_location_id` integer NOT NULL,
  `item_id` integer NOT NULL,
  `rank` text NOT NULL,
  `rare` integer NOT NULL,
  `node_type` integer NOT NULL,
  `stack_size` integer NOT NULL,
  `percentage` int(10) NOT NULL,
  foreign key(`meow_location_id`) references meow_location(`_id`),
  foreign key(`item_id`) references items(`_id`)
);

CREATE TABLE `monster_ailment` (
  `_id` integer primary key autoincrement,
  `monster_id` integer NOT NULL,
  `ailment` text NOT NULL,
  foreign key(`monster_id`) references monsters(`_id`)
);

CREATE TABLE `monster_damage` (
  `_id` integer primary key autoincrement,
  `monster_id` integer NOT NULL,
  `body_part` text NOT NULL,
  `cut`  integer DEFAULT NULL,
  `impact`  integer DEFAULT NULL,
  `shot`  integer DEFAULT NULL,
  `fire`  integer DEFAULT NULL,
  `water`  integer DEFAULT NULL,
  `ice`  integer DEFAULT NULL,
  `thunder`  integer DEFAULT NULL,
  `dragon`  integer DEFAULT NULL,
  `ko`  integer DEFAULT NULL,
  foreign key(`monster_id`) references monsters(`_id`)
);

CREATE TABLE `monster_habitat` (
  `_id` integer primary key autoincrement,
  `monster_id` integer NOT NULL,
  `location_id` integer NOT NULL,
  `start_area` integer DEFAULT NULL,
  `move_area` text DEFAULT NULL,
  `rest_area` integer DEFAULT NULL,
  foreign key(`location_id`) references locations(`_id`),
  foreign key(`monster_id`) references monsters(`_id`)
);

CREATE TABLE `monster_status` (
  `_id` integer primary key autoincrement,
  `monster_id` integer NOT NULL,
  `status` text NOT NULL,
  `initial` integer DEFAULT NULL,
  `increase` integer DEFAULT NULL,
  `max` integer DEFAULT NULL,
  `duration` integer DEFAULT NULL,
  `damage` integer DEFAULT NULL,
  foreign key(`monster_id`) references monsters(`_id`)
);

CREATE TABLE `monster_to_quest` (
  `_id` integer primary key autoincrement,
  `monster_id` integer NOT NULL,
  `quest_id` integer NOT NULL,
  `unstable` text,
  `hyper` integer NOT NULL,
  foreign key(`monster_id`) references monsters(`_id`),
  foreign key(`quest_id`) references quests(`_id`)
);

CREATE TABLE `monster_weakness` (
  `_id` integer primary key autoincrement,
  `monster_id` integer NOT NULL,
  `state` text NOT NULL,
  `fire` integer NOT NULL,
  `water` integer NOT NULL,
  `thunder` integer NOT NULL,
  `ice` integer NOT NULL,
  `dragon` integer NOT NULL,
  `poison` integer NOT NULL,
  `paralysis` integer NOT NULL,
  `sleep` integer NOT NULL,
  `pitfall_trap` integer NOT NULL,
  `shock_trap` integer NOT NULL,
  `flash_bomb` integer NOT NULL,
  `sonic_bomb` integer NOT NULL,
  `dung_bomb` integer NOT NULL,
  `meat` integer NOT NULL,
  foreign key(`monster_id`) references monsters(`_id`)
);

CREATE TABLE `monsters` (
  `_id` integer primary key autoincrement,
  `class` text NOT NULL,
  `name` text NOT NULL,
  `name_de` text NOT NULL,
  `name_fr` text NOT NULL,
  `name_es` text NOT NULL,
  `name_it` text NOT NULL,
  `name_ja` text NOT NULL,
  `base_hp` int NOT NULL,
  `icon_name` text DEFAULT NULL,
  `sort_name` text NOT NULL DEFAULT '',
  `metadata` int NOT NULL
);

CREATE TABLE `palico_armor` (
  `_id` integer primary key autoincrement,
  `defense` integer NOT NULL,
  `fire_res` integer NOT NULL,
  `thunder_res` integer NOT NULL,
  `dragon_res` integer NOT NULL,
  `water_res` integer NOT NULL,
  `ice_res` integer NOT NULL,
  `family` integer
);

CREATE TABLE `palico_weapons` (
  `_id` integer primary key autoincrement,
  `creation_cost` integer DEFAULT NULL,
  `attack_melee` integer NOT NULL,
  `attack_ranged` integer DEFAULT NULL,
  `element` text DEFAULT NULL,
  `element_melee` integer DEFAULT NULL,
  `element_ranged` integer DEFAULT NULL,
  `defense` integer DEFAULT NULL,
  `sharpness` integer DEFAULT NULL,
  `affinity_melee` integer NOT NULL,
  `affinity_ranged` integer NOT NULL,
  `blunt` integer NOT NULL,
  `balance` integer NOT NULL
);

CREATE TABLE `quest_rewards` (
  `_id` integer primary key autoincrement,
  `quest_id` integer NOT NULL,
  `item_id` integer NOT NULL,
  `reward_slot` text NOT NULL,
  `percentage` integer NOT NULL,
  `stack_size` integer NOT NULL,
  foreign key(`quest_id`) references quests(`_id`),
  foreign key(`item_id`) references items(`_id`)
);

CREATE TABLE `quests` (
  `_id` integer primary key autoincrement,
  `sort_order` integer NOT NULL,
  `name` text NOT NULL,
  `name_de` text NOT NULL,
  `name_fr` text NOT NULL,
  `name_es` text NOT NULL,
  `name_it` text NOT NULL,
  `name_ja` text DEFAULT NULL,
  `goal` text NOT NULL,
  `goal_de` text NOT NULL,
  `goal_fr` text NOT NULL,
  `goal_es` text NOT NULL,
  `goal_it` text NOT NULL,
  `goal_ja` text DEFAULT NULL,
  `hub` text NOT NULL,
  `type` text NOT NULL,
  `rank` text NOT NULL,
  `goal_type` integer DEFAULT 0,
  `hunter_type` integer NOT NULL,
  `stars` integer NOT NULL,
  `location_id` integer NOT NULL,
  `time_limit` integer NOT NULL,
  `fee` integer NOT NULL,
  `reward` mediumint(8) NOT NULL,
  `hrp` mediumint(8) DEFAULT NULL,
  `sub_goal` text DEFAULT NULL,
  `sub_goal_de` text NOT NULL,
  `sub_goal_fr` text NOT NULL,
  `sub_goal_es` text NOT NULL,
  `sub_goal_it` text NOT NULL,
  `sub_goal_ja` text DEFAULT NULL,
  `flavor` text DEFAULT NULL,
  `flavor_de` text NOT NULL,
  `flavor_fr` text NOT NULL,
  `flavor_es` text NOT NULL,
  `flavor_it` text NOT NULL,
  `flavor_ja` text DEFAULT NULL,
  `sub_reward` integer DEFAULT NULL,
  `sub_hrp` integer DEFAULT NULL,
  `permit_monster_id` integer,
  `metadata` integer NOT NULL,
  foreign key(`location_id`) references locations(`_id`),
  foreign key(`permit_monster_id`) references monsters(`_id`)
);

CREATE TABLE `skill_trees` (
  `_id` integer primary key autoincrement,
  `name` text NOT NULL,
  `name_de` text NOT NULL,
  `name_fr` text NOT NULL,
  `name_es` text NOT NULL,
  `name_it` text NOT NULL,
  `name_ja` text NOT NULL
);

CREATE TABLE `skills` (
  `_id` integer primary key autoincrement,
  `skill_tree_id` integer NOT NULL,
  `required_skill_tree_points` integer NOT NULL,
  `name` text NOT NULL,
  `name_de` text NOT NULL,
  `name_fr` text NOT NULL,
  `name_es` text NOT NULL,
  `name_it` text NOT NULL,
  `name_ja` text NOT NULL,
  `description` text NOT NULL,
  `description_de` text NOT NULL,
  `description_fr` text NOT NULL,
  `description_es` text NOT NULL,
  `description_it` text NOT NULL,
  `description_ja` text NOT NULL,
  foreign key(`skill_tree_id`) references skill_trees(`_id`)
);

CREATE TABLE `weapons` (
  `_id` integer primary key autoincrement,
  `parent_id` integer DEFAULT NULL,
  `wtype` text NOT NULL,
  `creation_cost` integer DEFAULT NULL,
  `upgrade_cost` integer DEFAULT NULL,
  `attack` integer NOT NULL,
  `max_attack` integer DEFAULT NULL,
  `element` text DEFAULT NULL,
  `element_attack` integer DEFAULT NULL,
  `element_2` text DEFAULT NULL,
  `element_2_attack` integer DEFAULT NULL,
  `awaken` text DEFAULT NULL,
  `awaken_attack` integer DEFAULT NULL,
  `defense` integer DEFAULT NULL,
  `sharpness` text DEFAULT NULL,
  `affinity` text NOT NULL,
  `horn_notes` text DEFAULT NULL,
  `shelling_type` text DEFAULT NULL,
  `phial` text DEFAULT NULL,
  `charges` text DEFAULT NULL,
  `coatings` text DEFAULT NULL,
  `recoil` text DEFAULT NULL,
  `reload_speed` text DEFAULT NULL,
  `rapid_fire` text DEFAULT NULL,
  `deviation` text DEFAULT NULL,
  `ammo` text DEFAULT NULL,
  `special_ammo` text DEFAULT NULL,
  `num_slots` integer NOT NULL,
  `tree_depth` integer NOT NULL,
  `final` integer,
  `family` integer
);

CREATE TABLE `wishlist` (
  `_id` integer primary key autoincrement,
  `name` text NOT NULL
);

CREATE TABLE `wishlist_component` (
  `_id` integer primary key autoincrement,
  `wishlist_id` integer NOT NULL,
  `component_id` integer NOT NULL,
  `quantity` integer NOT NULL,
  `notes` integer DEFAULT 0,
  foreign key (`wishlist_id`) references wishlist(`_id`),
  foreign key (`component_id`) references items(`_id`)
);

CREATE TABLE `wishlist_data` (
  `_id` integer primary key autoincrement,
  `wishlist_id` integer NOT NULL,
  `item_id` integer NOT NULL,
  `quantity` integer NOT NULL,
  `satisfied` integer DEFAULT 0,
  `path` text NOT NULL,
  foreign key (`wishlist_id`) references wishlist(`_id`),
  foreign key (`item_id`) references items(`_id`)
);

CREATE INDEX `ARMOR_TO_FAMILY_ID` ON `armor` (

    `family`    ASC

);
