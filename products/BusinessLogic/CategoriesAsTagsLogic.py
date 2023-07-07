

class CategoriesAsTagsLogic(object):

    def get_categories(self, collections):

        lst = []
        for collection in collections:
            main_category = collection.main_category.all()
            sub_category = collection.sub_category.all()
            super_sub_category = collection.super_sub_category.all()

            for i in main_category:
                lst.append(self.format_tag(i.name))
            for i in sub_category:
                lst.append(self.format_tag(i.name))
            for i in super_sub_category:
                lst.append(self.format_tag(i.name))

        return list(set(lst))

    def get_tags(self, product):

        db_tags = product.tag.all().values_list('name', flat=True)

        lst = []
        for category in self.get_categories(product.collection.all()):
            if category not in db_tags:
                lst.append(category)
        return lst

    @staticmethod
    def format_tag(tag):
        if tag != "":
            tag = list(tag)
            if tag[0] == ' ':
                tag[0] = ''
            if tag[len(tag) - 1] == ' ':
                tag[len(tag) - 1] = ''
            tag = "".join(tag)

        return tag
