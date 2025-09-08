# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import typing as t


class MenuItem:
    def __init__(
        self,
        id: str,
        label: str,
        icon: t.Optional[str] = None,
        disabled: t.Optional[bool] = False,
        children: t.Optional[t.List["MenuItem"]] = None,
    ):
        """
        :param id: Unique identifier for the menu item.
        :param label: Text label for the menu item.
        :param icon: Optional icon for the menu item.
        :param disabled: If True, the menu item is disabled. Can also be a string that evaluates to a boolean.
        :param children: Optional list of child menu items.
        """
        self.id = id
        self.label = label
        self.icon = icon
        self.disabled = disabled
        self.children = children if children is not None else []

    def _to_dict(self) -> t.Dict[str, t.Any]:
        """
        Convert the MenuItem to a dictionary representation.
        :return: Dictionary representation of the MenuItem.
        """
        return {
            "id": self.id,
            "label": self.label,
            "icon": self.icon,
            "disabled": self.disabled,
            "children": [child._to_dict() for child in self.children],
        }


def update_menu_item(menu_item: MenuItem, **kwargs) -> MenuItem:
    """
    Update the properties of a MenuItem instance.
    :param menu_item: The MenuItem instance to update.
    :param kwargs: Properties to update.
    :return: Updated MenuItem instance.
    """
    for key, value in kwargs.items():
        if hasattr(menu_item, key):
            setattr(menu_item, key, value)
    return menu_item


def find_menu_item_by_id(menu_items: t.List[MenuItem], item_id: str) -> t.Optional[MenuItem]:
    """
    Find a MenuItem by its ID in a list of MenuItems.
    :param menu_items: List of MenuItem instances.
    :param item_id: ID of the MenuItem to find.
    :return: The found MenuItem or None if not found.
    """
    for item in menu_items:
        if item.id == item_id:
            return item
        found = find_menu_item_by_id(item.children, item_id)
        if found:
            return found
    return None


def remove_menu_item_by_id(menu_items: t.List[MenuItem], item_id: str) -> bool:
    """
    Remove a MenuItem by its ID from a list of MenuItems.
    :param menu_items: List of MenuItem instances.
    :param item_id: ID of the MenuItem to remove.
    :return: True if the item was removed, False otherwise.
    """
    for i, item in enumerate(menu_items):
        if item.id == item_id:
            del menu_items[i]
            return True
        if remove_menu_item_by_id(item.children, item_id):
            return True
    return False


def add_menu_item(menu_items: t.List[MenuItem], new_item: MenuItem) -> None:
    """
    Add a new MenuItem to a list of MenuItems.
    :param menu_items: List of MenuItem instances.
    :param new_item: The new MenuItem to add.
    """
    menu_items.append(new_item)


def add_menu_item_to_parent(menu_items: t.List[MenuItem], parent_id: str, new_item: MenuItem) -> bool:
    """
    Add a new MenuItem to a specific parent MenuItem by ID.
    :param menu_items: List of MenuItem instances.
    :param parent_id: ID of the parent MenuItem to which the new item will be added.
    :param new_item: The new MenuItem to add.
    :return: True if the item was added, False if the parent was not found.
    """
    for item in menu_items:
        if item.id == parent_id:
            item.children.append(new_item)
            return True
        if add_menu_item_to_parent(item.children, parent_id, new_item):
            return True
    return False
