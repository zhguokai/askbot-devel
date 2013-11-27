from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError

class MergeRelationsCommand(BaseCommand):
    model = None #must assign to real model class in subclass
    print_warnings = True
    args = '<from_id> <to_id>'
    help = """Merge all relations to model assigned to object with id `from_id` to 
object with `to_id`, allows optional processing of custom fields of model
and potentially delete the older object"""

    def handle(self, *arguments, **options):

        if self.model is None:
            CommandError('Subclass of MergeRelationsCommand must define concrete "model"')

        self.parse_arguments(*arguments)

        for rel in self.model._meta.get_all_related_objects():
            self.process_related_objects(rel.model, rel.field.name)

        for rel in self.model._meta.get_all_related_many_to_many_objects():
            self.process_m2m_related_objects(rel.model, rel.field.name)

        self.process_fields()
        self.cleanup() 

    def cleanup(self):
        """this method must be implemented in the subclass,
        here you might delete the `from` object or log something, etc."""
        raise Exception, 'This method must be implemented'
      
    def process_fields(self):
        """Put model specific logic here.
        For example, model might have an integer field where
        you might want to add values of the two objects or 
        a char field were unique words need to be merged, etc.
        """
        pass

    def parse_arguments(self, *arguments):
        if len(arguments) != 2:
            raise CommandError('Arguments are <from_id> to <to_id>')
        self.from_object = self.model.objects.get(id = arguments[0])
        self.to_object = self.model.objects.get(id = arguments[1])

    def process_related_objects(self, model, field_name):
        """reassigns the related object to the new object"""
        filter_condition = {field_name: self.from_object}
        related_objects_qs = model.objects.filter(**filter_condition)
        print ('%s ' % unicode(model._meta)).encode('utf-8'),
        count = 0
        for related_object in related_objects_qs:
            setattr(related_object, field_name, self.to_object)
            try:
                related_object.validate_unique()
            except ValidationError, error:
                if self.print_warnings:
                    model_name = unicode(related_object._meta)
                    self.stderr.write((u'Warning: %s %s\n' % (model_name, error)).encode('utf-8'))
                continue
            related_object.save()
            count += 1

        self.stdout.write('%d\n' % count)

    def process_m2m_related_objects(self, model, field_name):
        """removes the old object from the M2M relation
        and adds the new object"""
        filter_condition = {field_name: self.from_object}
        related_objects_qs = model.objects.filter(**filter_condition)
        print ('%s ' % unicode(model._meta)).encode('utf-8'),
        count = 0
        for obj in related_objects_qs:
            m2m_field = getattr(obj, field_name)
            m2m_field.remove(self.from_object)
            try:
                m2m_field.add(self.to_object)
            except Exception, error:
                if self.print_warnings:
                    self.stderr.write((u'Warning: %s\n' % error).encode('utf-8'))
            count += 1

        self.stdout.write('%d\n' % count)
