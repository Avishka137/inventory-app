<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <div class="modal-title-wrap">
          <div class="modal-icon">{{ isEdit ? '✏️' : '✦' }}</div>
          <h2>{{ isEdit ? 'Edit Product' : 'New Product' }}</h2>
        </div>
        <button class="close-btn" @click="$emit('close')">
          <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M18 6L6 18M6 6l12 12"/></svg>
        </button>
      </div>

      <div class="form-grid">
        <div class="field">
          <label>Product Name *</label>
          <input v-model="form.name" placeholder="e.g. Wireless Mouse" />
        </div>
        <div class="field">
          <label>Category *</label>
          <input v-model="form.category" placeholder="e.g. Electronics" list="cat-list" />
          <datalist id="cat-list">
            <option value="Electronics"/><option value="Clothing"/><option value="Food & Beverage"/>
            <option value="Office Supplies"/><option value="Furniture"/><option value="Tools"/><option value="Other"/>
          </datalist>
        </div>
        <div class="field">
          <label>Quantity</label>
          <input v-model.number="form.quantity" type="number" min="0" placeholder="0" />
        </div>
        <div class="field">
          <label>Price (USD)</label>
          <input v-model.number="form.price" type="number" min="0" step="0.01" placeholder="0.00" />
        </div>
        <div class="field span-2">
          <label>Description</label>
          <textarea v-model="form.description" placeholder="Optional product description…" />
        </div>
      </div>

      <p v-if="error" class="error-msg">⚠ {{ error }}</p>

      <div class="modal-footer">
        <button class="btn btn-ghost" @click="$emit('close')">Cancel</button>
        <button class="btn btn-primary" @click="submit">
          {{ isEdit ? 'Save Changes' : 'Add Product' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
const props = defineProps({ product: Object });
const emit  = defineEmits(["save", "close"]);

const isEdit = computed(() => !!props.product?.id);
const form = ref({
  id:          props.product?.id          ?? null,
  name:        props.product?.name        ?? "",
  category:    props.product?.category    ?? "",
  quantity:    props.product?.quantity    ?? 0,
  price:       props.product?.price       ?? 0,
  description: props.product?.description ?? "",
});
const error = ref("");

function submit() {
  error.value = "";
  if (!form.value.name.trim())     { error.value = "Product name is required."; return; }
  if (!form.value.category.trim()) { error.value = "Category is required."; return; }
  if (form.value.quantity < 0)     { error.value = "Quantity cannot be negative."; return; }
  if (form.value.price < 0)        { error.value = "Price cannot be negative."; return; }
  emit("save", { ...form.value });
}
</script>

<style scoped>
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}
.modal-title-wrap { display: flex; align-items: center; gap: 12px; }
.modal-icon {
  width: 38px; height: 38px;
  background: rgba(99,102,241,0.15);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px;
}
.modal-header h2 { font-size: 18px; font-weight: 800; }

.close-btn {
  width: 32px; height: 32px;
  background: var(--surface2);
  border: 1px solid var(--border2);
  border-radius: 8px;
  color: var(--text2);
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all .15s;
}
.close-btn:hover { background: var(--surface3); color: var(--text); }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 20px; }
.span-2 { grid-column: span 2; }

.error-msg {
  color: var(--red);
  font-size: 13px;
  margin-bottom: 16px;
  background: rgba(248,113,113,0.1);
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid rgba(248,113,113,0.25);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
}
</style>