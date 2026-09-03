// Minimal helper: evaluate ACPI objects given by name and log them. Fails init on purpose so it never stays loaded.
#include <linux/module.h>
#include <linux/acpi.h>
static char *names[32];
static int n;
module_param_array(names, charp, &n, 0444);
static void show(const char *nm, union acpi_object *o, int depth)
{
	char pfx[16]; int i;
	snprintf(pfx, sizeof(pfx), "%*s", depth * 2, "");
	switch (o->type) {
	case ACPI_TYPE_INTEGER: pr_info("acpieval: %s%s = INT 0x%llx\n", pfx, nm, o->integer.value); break;
	case ACPI_TYPE_STRING: pr_info("acpieval: %s%s = STR \"%s\"\n", pfx, nm, o->string.pointer); break;
	case ACPI_TYPE_BUFFER:
		pr_info("acpieval: %s%s = BUF len %u\n", pfx, nm, o->buffer.length);
		print_hex_dump(KERN_INFO, "acpieval:   ", DUMP_PREFIX_OFFSET, 16, 1, o->buffer.pointer, o->buffer.length, false);
		break;
	case ACPI_TYPE_PACKAGE:
		pr_info("acpieval: %s%s = PKG count %u\n", pfx, nm, o->package.count);
		for (i = 0; i < o->package.count; i++) show("elem", &o->package.elements[i], depth + 1);
		break;
	case ACPI_TYPE_LOCAL_REFERENCE: {
		struct acpi_buffer b = { ACPI_ALLOCATE_BUFFER, NULL };
		if (ACPI_SUCCESS(acpi_get_name(o->reference.handle, ACPI_FULL_PATHNAME, &b))) {
			pr_info("acpieval: %s%s = REF %s\n", pfx, nm, (char *)b.pointer); kfree(b.pointer);
		}
		break; }
	default: pr_info("acpieval: %s%s = type %d\n", pfx, nm, o->type);
	}
}
static int __init ev_init(void)
{
	int i;
	for (i = 0; i < n; i++) {
		struct acpi_buffer buf = { ACPI_ALLOCATE_BUFFER, NULL };
		acpi_status st = acpi_evaluate_object(NULL, names[i], NULL, &buf);
		if (ACPI_FAILURE(st)) { pr_info("acpieval: %s -> %s\n", names[i], acpi_format_exception(st)); continue; }
		show(names[i], buf.pointer, 0);
		kfree(buf.pointer);
	}
	return -ENODEV;
}
module_init(ev_init);
MODULE_LICENSE("GPL");
