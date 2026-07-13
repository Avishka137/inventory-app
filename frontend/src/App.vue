<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="logo">
        <div class="logo-icon">▦</div>
        <div class="logo-text">Inven<span>tory</span></div>
      </div>
      <div class="nav-section-label">Main</div>
      <nav class="nav">
        <a class="nav-item active">
          <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M20 7H4a2 2 0 00-2 2v10a2 2 0 002 2h16a2 2 0 002-2V9a2 2 0 00-2-2z"/><path d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16"/></svg>
          Products
        </a>
      </nav>
      <div class="sidebar-stats">
        <div class="sidebar-stat">
          <span class="ss-label">Total Items</span>
          <span class="ss-val">{{ products.length }}</span>
        </div>
        <div class="sidebar-stat">
          <span class="ss-label">Total Value</span>
          <span class="ss-val">${{ totalValue }}</span>
        </div>
      </div>
      <div class="sidebar-footer">
        <div class="sf-dot"></div>
        Flask + Vue 3
      </div>
    </aside>

    <main class="main">
      <header class="topbar">
        <div class="topbar-left">
          <h1 class="page-title">Products</h1>
          <span class="page-pill">{{ filtered.length }} items</span>
        </div>
        <button class="btn btn-primary" @click="openCreate">
          <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>
          Add Product
        </button>
      </header>

      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon purple">
            <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16"/></svg>
          </div>
          <div>
            <div class="stat-label">Total Products</div>
            <div class="stat-val">{{ products.length }}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon teal">
            <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
          </div>
          <div>
            <div class="stat-label">Total Stock</div>
            <div class="stat-val">{{ totalStock }}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon amber">
            <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
          </div>
          <div>
            <div class="stat-label">Inventory Value</div>
            <div class="stat-val">${{ totalValue }}</div>
          </div>
        </div>
        <div class="stat-card" :class="{ danger: lowStock.length > 0 }">
          <div class="stat-icon red">
            <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          </div>
          <div>
            <div class="stat-label">Low Stock</div>
            <div class="stat-val" :class="{ 'val-danger': lowStock.length > 0 }">{{ lowStock.length }}</div>
          </div>
        </div>
      </div>

      <div class="toolbar">
        <div class="search-wrap">
          <svg class="search-icon" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
          <input v-model="search" class="search-input" placeholder="Search products..." />
        </div>
        <select v-model="filterCategory" class="filter-select">
          <option value="">All Categories</option>
          <option v-for="cat in categories" :key="cat">{{ cat }}</option>
        </select>
      </div>

      <div class="table-card">
        <div v-if="loading" class="empty-state">
          <div class="spinner"></div>
          Loading products...
        </div>
        <div v-else-if="filtered.length === 0" class="empty-state">
          <div class="empty-icon">📦</div>
          <p>No products found</p>
          <button class="btn btn-primary" @click="openCreate" style="margin-top:12px">Add your first product</button>
        </div>
        <table v-else class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Product</th>
              <th>Category</th>
              <th>Qty</th>
              <th>Price</th>
              <th>Description</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in filtered" :key="p.id" :class="{ 'row-low': p.quantity < 5 }">
              <td><span class="id-pill">#{{ p.id }}</span></td>
              <td class="td-name">{{ p.name }}</td>
              <td><span class="badge">{{ p.category }}</span></td>
              <td>
                <span class="qty-badge" :class="p.quantity < 5 ? 'qty-low' : 'qty-ok'">{{ p.quantity }}</span>
              </td>
              <td class="td-price">${{ p.price.toFixed(2) }}</td>
              <td class="td-desc">{{ p.description || '—' }}</td>
              <td>
                <div class="action-row">
                  <button class="btn btn-ghost btn-sm icon-btn" @click="openEdit(p)" title="Edit">
                    <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                  </button>
                  <button class="btn btn-danger btn-sm icon-btn" @click="confirmDelete(p)" title="Delete">
                    <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="3,6 5,6 21,6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/></svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>

    <ProductForm v-if="showForm" :product="editingProduct" @save="handleSave" @close="showForm = false" />

    <div class="modal-backdrop" v-if="deletingProduct" @click.self="deletingProduct = null">
      <div class="modal del-modal">
        <div class="del-icon">🗑️</div>
        <h2>Delete product?</h2>
        <p><strong>"{{ deletingProduct.name }}"</strong> will be permanently removed.</p>
        <div class="del-actions">
          <button class="btn btn-ghost" @click="deletingProduct = null">Cancel</button>
          <button class="btn btn-danger" @click="deleteProduct">Yes, delete it</button>
        </div>
      </div>
    </div>

    <div class="toast-wrap">
      <div v-for="t in toasts" :key="t.id" :class="['toast', t.type]">{{ t.message }}</div>
    </div>
<ChatBot />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import axios from "axios";
import ProductForm from "./components/ProductForm.vue";
import ChatBot from "./components/ChatBot.vue";

const products        = ref([]);
const loading         = ref(true);
const search          = ref("");
const filterCategory  = ref("");
const showForm        = ref(false);
const editingProduct  = ref(null);
const deletingProduct = ref(null);
const toasts          = ref([]);
const API = "https://avishka137.pythonanywhere.com/api";

const categories = computed(() => [...new Set(products.value.map(p => p.category))]);
const filtered   = computed(() => {
  let list = products.value;
  if (search.value) {
    const q = search.value.toLowerCase();
    list = list.filter(p => p.name.toLowerCase().includes(q) || p.category.toLowerCase().includes(q));
  }
  if (filterCategory.value) list = list.filter(p => p.category === filterCategory.value);
  return list;
});
const totalStock = computed(() => products.value.reduce((s, p) => s + p.quantity, 0));
const totalValue = computed(() => products.value.reduce((s, p) => s + p.quantity * p.price, 0).toFixed(2));
const lowStock   = computed(() => products.value.filter(p => p.quantity < 5));

async function fetchProducts() {
  loading.value = true;
  try {
    const { data } = await axios.get(`${API}/products`);
    products.value = data;
  } catch {
    toast("Cannot reach server. Is Flask running?", "error");
  } finally {
    loading.value = false;
  }
}

async function handleSave(formData) {
  try {
    if (formData.id) {
      const { data } = await axios.put(`${API}/products/${formData.id}`, formData);
      const idx = products.value.findIndex(p => p.id === data.id);
      products.value[idx] = data;
      toast("Product updated!", "success");
    } else {
      const { data } = await axios.post(`${API}/products`, formData);
      products.value.unshift(data);
      toast("Product added!", "success");
    }
    showForm.value = false;
  } catch (err) {
    toast(err.response?.data?.error || "Something went wrong.", "error");
  }
}

async function deleteProduct() {
  try {
    await axios.delete(`${API}/products/${deletingProduct.value.id}`);
    products.value = products.value.filter(p => p.id !== deletingProduct.value.id);
    toast("Product deleted.", "success");
  } catch {
    toast("Could not delete.", "error");
  } finally {
    deletingProduct.value = null;
  }
}

function openCreate()     { editingProduct.value = null; showForm.value = true; }
function openEdit(p)      { editingProduct.value = { ...p }; showForm.value = true; }
function confirmDelete(p) { deletingProduct.value = p; }

function toast(message, type = "success") {
  const id = Date.now();
  toasts.value.push({ id, message, type });
  setTimeout(() => { toasts.value = toasts.value.filter(t => t.id !== id); }, 3000);
}

onMounted(fetchProducts);
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 230px;
  background: var(--surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 24px 16px;
  position: sticky;
  top: 0;
  height: 100vh;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 8px;
  margin-bottom: 28px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: var(--accent);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  box-shadow: 0 0 20px var(--accent-glow);
}

.logo-text {
  font-size: 17px;
  font-weight: 800;
}

.logo-text span {
  color: var(--accent2);
}

.nav-section-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .12em;
  color: var(--text3);
  text-transform: uppercase;
  padding: 0 10px;
  margin: 4px 0 6px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text2);
  cursor: pointer;
  transition: all .15s;
  text-decoration: none;
}

.nav-item.active {
  background: rgba(99,102,241,0.12);
  color: var(--accent2);
}

.sidebar-stats {
  margin-top: auto;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sidebar-stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ss-label {
  font-size: 12px;
  color: var(--text3);
}

.ss-val {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
  font-family: var(--mono);
}

.sidebar-footer {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 11px;
  color: var(--text3);
  padding: 12px 10px 0;
  border-top: 1px solid var(--border);
  margin-top: 12px;
}

.sf-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 6px var(--green);
  flex-shrink: 0;
}

.main {
  flex: 1;
  padding: 32px 36px;
  overflow: auto;
  background: var(--bg);
  min-width: 0;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title {
  font-size: 26px;
  font-weight: 800;
}

.page-pill {
  background: var(--surface2);
  border: 1px solid var(--border2);
  border-radius: 20px;
  padding: 3px 12px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text2);
  font-family: var(--mono);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 14px;
}

.stat-card.danger {
  border-color: rgba(248,113,113,0.3);
}

.stat-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon.purple { background: rgba(99,102,241,0.15); color: var(--accent2); }
.stat-icon.teal   { background: rgba(45,212,191,0.12); color: var(--teal); }
.stat-icon.amber  { background: rgba(251,191,36,0.12); color: var(--amber); }
.stat-icon.red    { background: rgba(248,113,113,0.12); color: var(--red); }

.stat-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: .08em;
  margin-bottom: 4px;
}

.stat-val {
  font-size: 22px;
  font-weight: 800;
  font-family: var(--mono);
}

.val-danger { color: var(--red) !important; }

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.search-wrap {
  flex: 1;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text3);
  pointer-events: none;
}

.search-input {
  width: 100%;
  background: var(--surface);
  border: 1px solid var(--border2);
  border-radius: 12px;
  color: var(--text);
  font-family: var(--font);
  font-size: 13px;
  padding: 11px 16px 11px 40px;
  outline: none;
  transition: border .18s, box-shadow .18s;
  box-sizing: border-box;
}

.search-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-glow);
}

.filter-select {
  background: var(--surface);
  border: 1px solid var(--border2);
  border-radius: 12px;
  color: var(--text2);
  font-family: var(--font);
  font-size: 13px;
  padding: 11px 14px;
  outline: none;
  cursor: pointer;
  min-width: 160px;
}

.table-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

.table th {
  text-align: left;
  font-size: 10px;
  font-weight: 700;
  color: var(--text3);
  letter-spacing: .1em;
  text-transform: uppercase;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--surface2);
  white-space: nowrap;
}

.table td {
  padding: 13px 16px;
  font-size: 13px;
  border-bottom: 1px solid var(--border);
  vertical-align: middle;
}

.table tr:last-child td {
  border-bottom: none;
}

.table tbody tr {
  transition: background .15s;
}

.table tbody tr:hover td {
  background: var(--surface2);
}

.row-low td {
  background: rgba(248,113,113,0.03);
}

.id-pill {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text3);
  background: var(--surface2);
  padding: 2px 8px;
  border-radius: 6px;
}

.td-name { font-weight: 700; }

.td-price {
  font-family: var(--mono);
  font-size: 13px;
  color: var(--teal);
  font-weight: 600;
}

.td-desc {
  color: var(--text3);
  font-size: 12px;
  max-width: 160px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.qty-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  padding: 3px 10px;
  border-radius: 20px;
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 700;
}

.qty-ok  { background: rgba(52,211,153,0.12); color: var(--green); border: 1px solid rgba(52,211,153,0.2); }
.qty-low { background: rgba(248,113,113,0.12); color: var(--red); border: 1px solid rgba(248,113,113,0.2); }

.action-row {
  display: flex;
  gap: 6px;
}

.icon-btn {
  padding: 6px 8px !important;
}

.badge {
  background: rgba(99,102,241,0.12);
  color: var(--accent2);
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.empty-state {
  padding: 64px 32px;
  text-align: center;
  color: var(--text3);
  font-size: 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 4px;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 2px solid var(--border2);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin .7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.del-modal { text-align: center; max-width: 380px; }
.del-icon { font-size: 44px; margin-bottom: 12px; }
.del-modal h2 { font-size: 20px; font-weight: 800; margin-bottom: 8px; }
.del-modal p { color: var(--text2); font-size: 14px; margin-bottom: 24px; }
.del-actions { display: flex; justify-content: center; gap: 12px; }
</style>