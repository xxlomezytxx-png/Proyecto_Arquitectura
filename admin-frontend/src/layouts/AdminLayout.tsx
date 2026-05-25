import styles from "./AdminLayout.module.css";

const AdminLayout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className={styles.wrapper}>
      <aside className={styles.sidebar}>
        <div className={styles.logo}>📊 Pricing</div>
        <nav className={styles.nav}>
          <span className={styles.navItem}>Dashboard</span>
          <span className={`${styles.navItem} ${styles.active}`}>Pricing</span>
        </nav>
      </aside>

      <div className={styles.main}>
        <header className={styles.header}>
          <h1>Panel de Pricing</h1>
        </header>

        <section className={styles.content}>
          {children}
        </section>
      </div>
    </div>
  );
};

export default AdminLayout;